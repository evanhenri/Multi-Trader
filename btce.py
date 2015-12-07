import requests

from exchange import Exchange
import api_util

class TradeAPI(Exchange):
    def __init__(self):
        super(TradeAPI, self).__init__('btc-e')
        self.trade_api_url = 'https://btc-e.com/tapi'
    def trade_api_request(self, command, payload={}):
        payload['method'] = command
        resp = self.session.post(self.trade_api_url, data=payload, auth=api_util.Auth(self.key, self.secret, self.exchange_name))
        response = resp.json()
        return response
    def getInfo(self):
        return self.trade_api_request('getInfo')
    def TransHistory(self):
        return self.trade_api_request('TransHistory')
    def TradeHistory(self):
        return self.trade_api_request('TradeHistory')
    def ActiveOrders(self, pair=None):
        params = {}
        if pair: params['pair'] = pair
        return self.trade_api_request('ActiveOrders', params)
    def Trade(self, pair, trade_type, rate, amount):
        return self.trade_api_request('Trade', {'pair':pair,
                                                'type':trade_type,
                                                'rate':rate,
                                                'amount':amount})
    def CancelOrder(self, order_id):
        return self.trade_api_request('CancelOrder', {'order_id':order_id})

class PublicAPI(object):
    def __init__(self):
        self.public_api_url = 'https://btc-e.com/api/3/'

    def public_api_request(self, command, payload=[]):
        for param in payload:
            command += '/' + param
        return requests.get(self.public_api_url + command).text
    def info(self):
        return self.public_api_request('info')
    def ticker(self, currency_pair):
        return self.public_api_request('ticker', [currency_pair.lower()])
    def depth(self, currency_pair):
        return self.public_api_request('depth', [currency_pair.lower()])
    def trades(self, currency_pair):
        return self.public_api_request('trades', [currency_pair.lower()])