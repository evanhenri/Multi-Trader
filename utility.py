from datetime import datetime
from collections import deque
import re

def swap(lst, lhs, rhs):
    """
    swap first instance lhs with first instance of rhs in lst
    """
    lhs_index, rhs_index = lst.index(lhs), lst.index(rhs)
    lst[lhs_index], lst[rhs_index] = lst[rhs_index], lst[lhs_index]
    return lst

def first_non_digit(string):
    if string.isnumeric():
        return None
    for char in string:
        if not char.isnumeric():
            return char

def non_alpha_to_ws(string):
    return re.sub(r'\D', ' ', string)


def fill_remainder(lst, size, filler, front=False):
    """
    Fills contents of lst with filler until it is of length size-1
    Extends lst by default unless front is True
    """
    if len(lst) != size - 1:
        seq = [filler] * (size - len(lst))
        if front:
            deq = deque(lst)
            deq.extendleft(seq)
            lst = list(deque(deq))
        else:
            lst.extend(seq)
    return lst

def date_to_timestamp(calendar_date):
    """
    Takes date as elements delimited by non-numbers in format yyyy-mm-dd and returns time since epoch as integer
    Produces correct values as long as date elements are separated by non-numeric characters, e.g. 1990/5-31 1990*5!31
    """
    date_ws = non_alpha_to_ws(calendar_date)
    date_lst = [int(i) for i in date_ws.split(' ') if len(i) > 0]
    d = fill_remainder(date_lst, 6, 0)
    return (datetime(d[0], d[1], d[2], d[3], d[4], d[5]) - datetime(1970,1,1)).total_seconds()

def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False