# -*- coding: utf-8 -*-
DBG_COUNTER = 1   # this makes a new user on every call.


def find_username(start_data):
    """Return a local user name from information in ``start_data``.
       (The default django User.username field is 30 characters, which is
       less than the 34 characters in start_data['persnr']..)
    """
    global DBG_COUNTER
    uname = 'fin-tool-' + start_data['persnr'][:10] + '%03d' % DBG_COUNTER
    DBG_COUNTER += 1
    return uname
