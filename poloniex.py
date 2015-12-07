import requests
import time
from collections import OrderedDict

from exchange import Exchange
import api_util

class TradeAPI(Exchange):
    def __init__(self):
        super(TradeAPI, self).__init__('poloniex')
        self.trade_api_url = 'https://poloniex.com/tradingApi'

    def trade_api_request(self, command, payload={}):
        payload['command'] = command
        resp = self.session.post(self.trade_api_url, data=payload, auth=api_util.Auth(self.key, self.secret, self.exchange_name))
        return resp.json()

    def returnBalances(self):
        return self.trade_api_request('returnBalances')

    def returnCompleteBalances(self):
        return self.trade_api_request('returnCompleteBalances')

    def returnDepositAddresses(self):
        return self.trade_api_request('returnDepositAddresses')

    def generateNewAddress(self, currency):
        return self.trade_api_request('generateNewAddress', {'currency':currency})

    def returnDepositsWithdrawals(self, start, end=time.time()):
        start = str(api_util.get_date(start))
        end = str(api_util.get_date(end))
        return self.trade_api_request('returnDepositsWithdrawals', {'start':start,
                                                                    'end':end})

    def returnOpenOrders(self, currency_pair='all'):
        return self.trade_api_request('returnOpenOrders', {'currencyPair':currency_pair})

    def returnTradeHistory(self, currency_pair='all', start=None, end=time.time()):
        params = {'currencyPair':currency_pair}
        if start:
            params['start'] = str(api_util.get_date(start))
            params['end'] = str(api_util.get_date(end))
        return self.trade_api_request('returnTradeHistory', params)

    def buy(self, currency_pair, rate, amount):
        return self.trade_api_request('buy', {'currencyPair':currency_pair,
                                              'rate':rate,
                                              'amount':amount})

    def sell(self, currency_pair, rate, amount):
        return self.trade_api_request('sell', {'currencyPair':currency_pair,
                                              'rate':rate,
                                              'amount':amount})

    def cancel_order(self, orderNumber):
        return self.trade_api_request('cancelOrder', {'orderNumber':orderNumber})

    def move_order(self, orderNumber, rate, amount=None):
        params = {'orderNumber':orderNumber,
                  'rate':rate}
        if amount: params['amaount'] = amount
        return self.trade_api_request('moveOrder', params)

    def withdraw(self, currency, amount, address, paymentId=None):
        params = {'currency':currency,
                  'amount':amount,
                  'address':address}
        if paymentId: params['paymentID'] = paymentId
        return self.trade_api_request('withdraw', params)

    def returnAvailableAccountBalances(self, account=None):
        params = {}
        if account: params['account'] = account
        return self.trade_api_request('returnAvailableAccountBalances', params)

    def returnTradableBalances(self):
        return self.trade_api_request('returnTradableBalances')

    def transferBalance(self, currency, amount, fromAccount, toAccount):
        return self.trade_api_request('transferBalance', {'currency':currency,
                                                          'amount':amount,
                                                          'fromAccount':fromAccount,
                                                          'toAccount':toAccount})

    def returnMarginAccountSummary(self):
        return self.trade_api_request('returnMarginAccountSummary')

    def marginBuy(self, currencyPair, rate, amount, lendingRate=None):
        params = {'currencyPair':currencyPair,
                  'rate':rate,
                  'amount':amount}
        if lendingRate: params['lendingRate'] = lendingRate
        return self.trade_api_request('marginBuy', params)

    def marginSell(self, currencyPair, rate, amount, lendingRate=None):
        params = {'currencyPair':currencyPair,
                  'rate':rate,
                  'amount':amount}
        if lendingRate: params['lendingRate'] = lendingRate
        return self.trade_api_request('marginSell', params)

    def getMarginPosition(self, currencyPair='all'):
        return self.trade_api_request('getMarginPosition', {'currencyPair':currencyPair})

    def closeMarginPosition(self, currencyPair):
        return self.trade_api_request('closeMarginPosition', {'currencyPair':currencyPair})

    def createLoanOffer(self, currency, amount, duration, autorenew, lendingRate):
        return self.trade_api_request('createLoanOffer', {'currency':currency,
                                                          'amount':amount,
                                                          'duration':duration,
                                                          'autorenew':autorenew,
                                                          'lendingRate':lendingRate})

    def cancelLoanOffer(self, orderNumber):
        return self.trade_api_request('cancelLoanOffer', {'orderNumber':orderNumber})

    def returnOpenLoanOffers(self):
        return self.trade_api_request('returnOpenLoanOffers')

    def returnActiveLoans(self):
        return self.trade_api_request('returnActiveLoans')

    def toggleAutoRenew(self, orderNumber):
        return self.trade_api_request('toggleAutoRenew', {'orderNumber':orderNumber})

class PublicAPI(object):
    def __init__(self):
        self.public_api_url = 'http://poloniex.com/public?command='

    def public_api_request(self, command, payload={}):
        for k, v in payload.items():
            command += '&' + k + '=' + v
        return requests.get(self.public_api_url + command).text

    def returnTicker(self):
        return self.public_api_request('returnTicker')

    def return24Volume(self):
        return self.public_api_request('return24Volume')

    def returnOrderBook(self, currencyPair='all', depth=50):
        payload = OrderedDict([('currencyPair', currencyPair),
                               ('depth', str(depth))])
        return self.public_api_request('returnOrderBook', dict(payload))

    def returnTradeHistory(self, currencyPair, start, end):
        payload = OrderedDict([('currencyPair', currencyPair),
                               ('start', str(api_util.get_date(start))),
                               ('end', str(api_util.get_date(end)))])
        return self.public_api_request('returnTradeHistory', dict(payload))

    def returnChartData(self, currencyPair, period, start, end):
        payload = OrderedDict([('currencyPair', currencyPair),
                               ('start', str(api_util.get_date(start))),
                               ('end', str(api_util.get_date(end))),
                               ('period', period)])
        return self.public_api_request('returnChartData', dict(payload))

    def returnCurrencies(self):
        return self.public_api_request('returnCurrencies')

    def returnLoanOrders(self, currency):
        return self.public_api_request('returnLoanOrders', {'currency':currency})
