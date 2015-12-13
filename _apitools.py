import os
import re
import json
import hmac
import hashlib
from datetime import datetime
from collections import deque
from requests.auth import AuthBase

class Auth(AuthBase):
    def __init__(self, key, secret, nonce):
        self.key = key
        self.secret = secret
        self.nonce = nonce
    def __call__(self, r):
        r.body += '&nonce=%d' % self.nonce
        r.headers['Key'] = self.key
        r.headers['Sign'] = hmac.new(self.secret, r.body.encode('utf-8'), hashlib.sha512).hexdigest()
        return r

def get_nonce(nonce_file_path):
    with open(nonce_file_path, 'r+') as f:
        nonce = json.load(f)
        current_nonce = int(nonce['nonce'])
        next_nonce = {'nonce':current_nonce + 1}
        formatted_json = json.dumps(next_nonce, indent=4, sort_keys=True)
        f.seek(0)
        f.write(formatted_json)
    f.close()
    return current_nonce

def get_key(exchange):
    credentials_file = os.path.dirname(os.path.abspath(__file__)) + '/credentials.json'
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
    f.close()
    return credentials[exchange]['key']

def get_secret(exchange):
    credentials_file = os.path.dirname(os.path.abspath(__file__)) + '/credentials.json'
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
    f.close()
    return credentials[exchange]['secret']

def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False

def non_numeric_filter(s, filler=' '):
    """ replaces all non-numeric characters in string s with whitespace """
    return re.sub(r'\D', filler, s)

def swap(x, y, lst):
    """ swap first instance of x with first instance of y in lst """
    x_index, y_index = lst.index(x), lst.index(y)
    lst[x_index], lst[y_index] = lst[y_index], lst[x_index]
    return lst

def lr_fill(seq, max_length, filler, front=False):
    """
    Fills contents of seq with filler until len(seq) == max_length-1
    Extends seq backward by default unless front is True
    """
    if len(seq) < max_length:
        fill = [filler] * (max_length - len(seq))
        if front:
            if type(seq) is str:
                seq = ''.join(fill) + seq
            if type(seq) is list:
                deq = deque(seq)
                deq.extendleft(fill)
                seq = list(deque(deq))
        else:
            if type(seq) is str:
                seq += ''.join(fill)
            if type(seq) is list:
                seq += fill
    return seq

def date_to_timestamp(calendar_date):
    """
    Takes date as elements delimited by non-numbers in format yyyy-mm-dd and returns time since epoch as integer
    Produces correct values as long as date elements are separated by non-numeric characters, e.g. 1990/5-31 1990*5!31
    """
    date_ws = non_numeric_filter(calendar_date)
    date_lst = [int(i) for i in date_ws.split(' ') if len(i) > 0]
    if len(date_lst) == 3:
        for d in date_lst:
            if d > 31:
                date_lst = swap(d, date_lst[0], date_lst)
            elif 12 < d < 28:
                date_lst = swap(d, date_lst[2], date_lst)

    d = lr_fill(date_lst, 6, 0)
    return (datetime(d[0], d[1], d[2], d[3], d[4], d[5]) - datetime(1970,1,1)).total_seconds()

def date_to_unix_timestamp(date):
    if is_float(date):
        return float(date)
    else:
        return date_to_timestamp(date)