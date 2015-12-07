import os
import json
import api_util
import requests

class Exchange(object):
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.key = api_util.get_key(self.exchange_name).encode('utf-8')
        self.secret = api_util.get_secret(self.exchange_name).encode('utf-8')
        self.session = requests.Session()
        self.verify_nonce_file()
    def verify_nonce_file(self):
        nonce_path = 'nonce/' + self.exchange_name + '.json'
        if not os.path.isfile(nonce_path):
            with open(nonce_path, 'w') as f:
                payload = { 'nonce':0 }
                json.dump(payload, f)
            f.close()