from . import _apitools
import requests

def public_api_request(command, payload=[]):
    public_api_url = 'https://btc-e.com/api/3/'
    for param in payload:
        command += '/' + param
    try:
        resp = requests.get(public_api_url + command).text
        return resp
    except requests.Timeout as e:
        print('Post timeout', e.args)
    except requests.ConnectionError as e:
        print('Unable to connect to network', e.args)
    exit()

def exchange_info():
    return public_api_request('info')
def ticker(currency_pair):
    return public_api_request('ticker', [currency_pair.lower()])
def depth(currency_pair):
    return public_api_request('depth', [currency_pair.lower()])
def trade_history(currency_pair):
    return public_api_request('trades', [currency_pair.lower()])

class TradeAPI(object):
    def __init__(self, api_key, api_secret, nonce_path):
        self.api_key = api_key.encode('utf-8')
        self.api_secret = api_secret.encode('utf-8')
        self.nonce_path = nonce_path
        self.trade_api_url = 'https://btc-e.com/tapi'
        self.session = requests.Session()

    def trade_api_request(self, command, payload={}):
        payload['method'] = command
        nonce = _apitools.get_nonce(self.nonce_path)
        try:
            resp = self.session.post(self.trade_api_url,
                                     data=payload,
                                     auth=_apitools.Auth(self.api_key, self.api_secret, nonce))
            response = resp.json()
            return response
        except requests.Timeout as e:
            print('Post timeout', e.args)
        except requests.ConnectionError as e:
            print('Unable to connect to network', e.args)
        exit()

    def user_info(self):
        return self.trade_api_request('getInfo')

    def tx_history(self):
        return self.trade_api_request('TransHistory')

    def trade_history(self):
        return self.trade_api_request('TradeHistory')

    def active_orders(self, pair=None):
        params = {}
        if pair: params['pair'] = pair
        return self.trade_api_request('ActiveOrders', params)

    def buy(self, pair, rate, amount):
        return self.trade_api_request('Trade', {'pair':pair,'type':'buy','rate':rate,'amount':amount})

    def sell(self, pair, rate, amount):
        return self.trade_api_request('Trade', {'pair':pair,'type':'sell','rate':rate,'amount':amount})

    def cancel_order(self, order_id):
        return self.trade_api_request('CancelOrder', {'order_id':order_id})