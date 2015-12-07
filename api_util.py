import os
import json
import hmac
import hashlib
from requests.auth import AuthBase

import utility

class Auth(AuthBase):
    def __init__(self, key, secret, exchange_name):
        self.key = key
        self.secret = secret
        self.nonce = get_nonce(exchange_name)
    def __call__(self, r):
        r.body += '&nonce=%d' % self.nonce
        r.headers['Key'] = self.key
        r.headers['Sign'] = hmac.new(self.secret, r.body.encode('utf-8'), hashlib.sha512).hexdigest()
        return r

def init_config():
    if not os.path.isdir('nonce'):
        os.mkdir('nonce')
    if not os.path.isfile('credentials.json') or os.path.getsize('credentials.json') == 0:
        with open('credentials.json', 'w') as f:
            payload = { 'api_key:123':123, 'secret':456 }
            json.dump(payload, f)
        f.close()

def get_nonce(exhange):
    with open('nonce/' + exhange + '.json', 'r+') as f:
        nonce = json.load(f)
        current_nonce = int(nonce['nonce'])
        next_nonce = {'nonce':current_nonce + 1}
        formatted_json = json.dumps(next_nonce, indent=4, sort_keys=True)
        f.seek(0)
        f.write(formatted_json)
    f.close()
    return current_nonce

def get_key(exchange):
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)
    f.close()
    return credentials[exchange]['key']

def get_secret(exchange):
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)
    f.close()
    return credentials[exchange]['secret']

def get_date(date_arg):
        if utility.is_float(date_arg):
            return float(date_arg)
        else:
            return utility.date_to_timestamp(date_arg)