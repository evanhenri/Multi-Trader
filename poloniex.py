from . import _apitools

import requests
import time
import json
from collections import OrderedDict
from decimal import Decimal

def public_api_request(command, payload={}):
    public_api_url = 'http://poloniex.com/public?command='
    for k, v in payload.items():
        command += '&' + str(k) + '=' + str(v)
    try:
        resp = json.loads(requests.get(public_api_url + command, timeout=10).text)
        return resp
    except requests.Timeout as e:
        print('Post timeout', e.args)
    except requests.ConnectionError as e:
        print('Unable to connect to network', e.args)
    exit()

def ticker():
    return public_api_request('returnTicker')

def vol_24hr():
    return public_api_request('return24Volume')

def order_book(currency_pair='all', depth=50):
    payload = OrderedDict([('currencyPair', currency_pair.upper()), ('depth', str(depth))])
    return public_api_request('returnOrderBook', dict(payload))

def bid_orders(currency_pair):
    bids = order_book(currency_pair)['bids']
    bids.sort(key=lambda x: x[0])
    return bids

def ask_orders(currency_pair):
    asks = order_book(currency_pair)['asks']
    asks.sort(key=lambda x: x[0])
    return asks

def trade_history(currency_pair, start, end):
    payload = {'currencyPair':currency_pair.upper(),
               'start':_apitools.date_to_unix_timestamp(start),
               'end':_apitools.date_to_unix_timestamp(end)}
    return public_api_request('returnTradeHistory', payload)

def chart_data(currency_pair, period, start, end):
    valid_periods = ['300', '900', '1800', '7200', '14400', '86400']
    if str(period) in valid_periods:
        payload = {'currencyPair':currency_pair.upper(),
                   'start':_apitools.date_to_unix_timestamp(start),
                   'end':_apitools.date_to_unix_timestamp(end), 'period':period}
        return public_api_request('returnChartData', payload)
    else:
        print('Invalid arg \'{arg}\', valid periods: {lst}'.format(arg=period, lst=[p for p in valid_periods]))
        exit()

def exchange_info():
    return public_api_request('returnCurrencies')

def loan_orders(currency):
    return public_api_request('returnLoanOrders', {'currency':currency.upper()})

class TradeAPI(object):
    def __init__(self, api_key, api_secret, nonce_path):
        self.api_key = api_key.encode('utf-8')
        self.api_secret = api_secret.encode('utf-8')
        self.nonce_path = nonce_path
        self.trade_api_url = 'https://poloniex.com/tradingApi'
        self.session = requests.Session()

    def trade_api_request(self, command, payload={}):
        payload['command'] = command
        nonce = _apitools.get_nonce(self.nonce_path)
        try:
            resp = self.session.post(self.trade_api_url,
                                     data=payload,
                                     auth=_apitools.Auth(self.api_key, self.api_secret, nonce),
                                     timeout=10)
            return resp.json()
        except requests.Timeout as e:
            print('Post timeout', e.args)
        except requests.ConnectionError as e:
            print('Unable to connect to network', e.args)
        exit()

    def balances(self):
        return self.trade_api_request('returnBalances')

    def balance(self, currency):
        balances = self.balances()
        for coin, qty in balances.items():
            if coin == currency.upper():
                return qty

    def complete_balances(self):
        return self.trade_api_request('returnCompleteBalances')

    def deposit_addresses(self):
        return self.trade_api_request('returnDepositAddresses')

    def generate_deposit_address(self, currency):
        return self.trade_api_request('generateNewAddress', {'currency':currency.upper()})

    def deposits_withdrawals(self, start, end=time.time()):
        start = str(_apitools.date_to_unix_timestamp(start))
        end = str(_apitools.date_to_unix_timestamp(end))
        return self.trade_api_request('returnDepositsWithdrawals', {'start':start, 'end':end})

    def open_order(self, currency_pair='all'):
        return self.trade_api_request('returnOpenOrders', {'currencyPair':currency_pair.upper()})

    def trade_history(self, currency_pair='all', start=None, end=time.time()):
        params = {'currencyPair':currency_pair.upper()}
        if start:
            params['start'] = str(_apitools.date_to_unix_timestamp(start))
            params['end'] = str(_apitools.date_to_unix_timestamp(end))
        return self.trade_api_request('returnTradeHistory', params)

    def buy(self, currency_pair, rate, amount):
        return self.trade_api_request('buy', {'currencyPair':currency_pair.upper(), 'rate':rate, 'amount':amount})

    def tradable_balance(self, from_currency, trade_quantity=None):
        balance = self.balance(from_currency.upper())
        if trade_quantity and Decimal(balance) > trade_quantity:
            return trade_quantity
        return balance

    def market_order_buy(self, from_currency, currency_pair, buy_quantity):
        balance = self.tradable_balance(from_currency.upper(), buy_quantity)
        asks = ask_orders(currency_pair.upper())
        while balance > 0 and len(asks) > 0:
            top_rate, top_amount = asks.pop()
            if Decimal(balance) > Decimal(top_amount):
                self.buy(currency_pair='BTC_LTBC', rate=top_rate, amount=top_amount)
            else:
                self.buy(currency_pair='BTC_LTBC', rate=top_rate, amount=buy_quantity)
            buy_quantity -= top_amount

    def sell(self, currency_pair, rate, amount):
        return self.trade_api_request('sell', {'currencyPair':currency_pair.upper(), 'rate':rate, 'amount':amount})

    def market_order_sell(self, from_currency, currency_pair, sell_quantity):
        balance = self.tradable_balance(from_currency, sell_quantity)
        if sell_quantity > balance:
            sell_quantity = balance
        bids = bid_orders(currency_pair.upper())
        bids.sort(key=lambda x: Decimal(x[0]))
        bids = [(_apitools.truncate_decimal(rate, 8), _apitools.truncate_decimal(qty, 8),) for rate,qty in bids]

        while sell_quantity > 0 and len(bids) > 0:
            top_bid = bids.pop()
            top_rate, top_amount = Decimal(top_bid[0]), Decimal(top_bid[1])
            if sell_quantity > top_amount:
                self.sell(currency_pair='BTC_LTBC', rate=top_rate, amount=top_amount)
            else:
                self.sell(currency_pair='BTC_LTBC', rate=top_rate, amount=sell_quantity)
            sell_quantity -= top_amount

    def cancel_order(self, order_number):
        return self.trade_api_request('cancelOrder', {'orderNumber':order_number})

    def move_order(self, order_number, rate, amount=None):
        params = {'orderNumber':order_number,'rate':rate}
        if amount: params['amaount'] = amount
        return self.trade_api_request('moveOrder', params)

    def withdraw(self, currency, amount, address, payment_id=None):
        params = {'currency':currency,'amount':amount,'address':address}
        if payment_id: params['paymentID'] = payment_id
        return self.trade_api_request('withdraw', params)

    def available_account_balances(self, account=None):
        params = {}
        if account: params['account'] = account
        return self.trade_api_request('returnAvailableAccountBalances', params)

    def tradable_margin_balances(self):
        return self.trade_api_request('returnTradableBalances')

    def transfer_balance(self, currency, amount, from_account, to_account):
        return self.trade_api_request('transferBalance', {'currency':currency,
                                                          'amount':amount,
                                                          'fromAccount':from_account,
                                                          'toAccount':to_account})

    def margin_account_summary(self):
        return self.trade_api_request('returnMarginAccountSummary')

    def margin_buy(self, currencyPair, rate, amount, lending_rate=None):
        params = {'currencyPair':currencyPair,'rate':rate,'amount':amount}
        if lending_rate: params['lendingRate'] = lending_rate
        return self.trade_api_request('marginBuy', params)

    def margin_sell(self, currencyPair, rate, amount, lending_rate=None):
        params = {'currencyPair':currencyPair,'rate':rate,'amount':amount}
        if lending_rate: params['lendingRate'] = lending_rate
        return self.trade_api_request('marginSell', params)

    def margin_position(self, currency_pair='all'):
        return self.trade_api_request('getMarginPosition', {'currencyPair':currency_pair})

    def close_margin_position(self, currency_pair):
        return self.trade_api_request('closeMarginPosition', {'currencyPair':currency_pair})

    def create_loan_offer(self, currency, amount, duration, autorenew, lending_rate):
        return self.trade_api_request('createLoanOffer', {'currency':currency,
                                                          'amount':amount,
                                                          'duration':duration,
                                                          'autorenew':autorenew,
                                                          'lendingRate':lending_rate})

    def cancel_loan_offer(self, order_number):
        return self.trade_api_request('cancelLoanOffer', {'orderNumber':order_number})

    def open_loan_offers(self):
        return self.trade_api_request('returnOpenLoanOffers')

    def active_loans(self):
        return self.trade_api_request('returnActiveLoans')

    def auto_renew(self, order_number):
        return self.trade_api_request('toggleAutoRenew', {'orderNumber':order_number})

