# -*- coding: utf-8 -*-
import datetime
import json
import random
import requests
import dkredis
from django import http

from . import appsettings


class ToolCallError(Exception):
    """Generic toolcall error.
    """
    def __init__(self, error='', msg='', token=''):
        self.error = error
        self.msg = msg
        self.token = token


def error_response(toolerr):
    """Convenience function to create a response from an exception.
    """
    return http.HttpResponse("ERROR (%s): %s<br>(token: %s)" % (
        toolerr.error,
        toolerr.msg,
        toolerr.token
    ))


def get_start_token(request):
    """Returns the start token from the request.
    """
    token = request.REQUEST['access_token']
    # check if token has been seen before..
    return token


def fetch_start_data(start_token):
    """Send ``start_token`` to toolcall server and return the ``start_data``.
       Raises a :class:`ToolCallError` if something goes wrong.
    """
    url = appsettings.TOOLCALL_FETCH_START_DATA_URL
    url += '?access_token=' + start_token
    r = requests.get(url)

    # check the status code.
    if r.status_code != 200:
        raise ToolCallError(
            error=r.status_code,
            msg="%s did not return 200 OK, it returned %s." % (
                appsettings.TOOLCALL_FETCH_START_DATA_URL,
                r.status_code
            ),
            token=start_token
        )

    start_data = r.json()
    if start_data['type'] == 'error':
        raise ToolCallError(
            error=start_data['data']['error'],
            msg=start_data['data']['msg'],
            token=start_token
        )

    return start_data['data']


def send_result_token(request, correct):
    """Store the result data, and send the result token to the toolcall server.
    """
    token = str(random.randrange(2**16, 2**32))

    start = request.session['start-data']
    result_data = {
        'type': 'result',
        'token': token,
        'timestamp': datetime.datetime.now().isoformat(),
        'data': {
            'persnr': start['persnr'],
            'participant_id': str(request.user.id),      # client-local ID
            'exam': start['exam'],  # (my-tool)
            'passed': correct,         # did the user pass the test
            "score": 100 if correct else 0,
            "system": start['system'],
            "exam_type": start["exam_kind"]  # historical accident..
        }
    }
    print "STORING:RESULT:", json.dumps(result_data, indent=4)
    dkredis.set_pyval('CLIENT-TOKEN-' + token,
                      result_data,
                      200)  # seconds

    url = appsettings.RESULT_TOKEN_URL
    url += '?access_token=' + token
    url += '&client=' + appsettings.CLIENT_NAME

    r = requests.get(url)

    # check the status code.
    if r.status_code != 200:
        raise ToolCallError(
            error=r.status_code,
            msg="%s did not return 200 OK, it returned %s." % (
                appsettings.RESULT_TOKEN_URL,
                r.status_code
            ),
            token=token
        )
