# -*- coding: utf-8 -*-
import datetime
import json
import random

import requests
from django import http

# (http://localhost:8000/.api/toolcall/v2/) api.urls.root-url
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import dkredis
import logging

from django.views.decorators.csrf import csrf_exempt

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
# import toolcall

from . import appsettings


# (http://localhost:8000/.api/toolcall/v2/) api.urls.result_token.url
RESULT_TOKEN_URL = 'result/'


def receive_start_token(request):
    token = request.REQUEST['access_token']
    # check if token has been seen before..?
    url = appsettings.START_DATA_URL + '?access_token=' + token

    # return token and get start data
    print "FETCHING:", url
    # log.debug("fetching %r", url)
    r = requests.get(url)
    if r.status_code != 200:
        print '\n'*12, "ERROR", '\n'*10
        print r.text
        raise ValueError(str(r.status_code))
        # response = http.HttpResponseServerError(r.text)
        # return response

    print "STATUS_CODE:", `r.status_code`
    start_data = r.json()
    print "START-DATA:", json.dumps(start_data, indent=4)

    if start_data['type'] == 'error':
        # display errors to user (with token) if you can't handle the error
        # in a reasonable fashion
        return http.HttpResponse("ERROR (%s): %s<br>(%s)" % (
            start_data['data']['error'],
            start_data['data']['msg'],
            start_data['token']
        ))

    # Note: you have to return start_data['system'] with your result data.
    #       Here I log the user in and save it in their session, there are
    #       probably other/better ways to do this.

    # must start with a finaut prefix since we're using an internal blindsso
    # authenticator here
    username = 'fin-tool-' + start_data['data']['persnr'][:15]
    # create user if new
    if not User.objects.filter(username=username):
        User.objects.create_user(
            username=username,
            first_name=start_data['data']['firstName'],
            last_name=start_data['data']['lastName'],
        )

    # this authenticate should end up in
    # toolcall.auth_backend.DKSSOBlindTrustAuthenticator
    # (you can also "cheat" by setting user.backend directly insted..)
    user = authenticate(username=username, sso_login=True)
    if user is None or not user.is_active:
        raise ValueError("user couln't authenticate: " + username)
    # user = User.objects.get(username=username)
    # user.backend = ModelBackend
    login(request, user)
    user = request.user
    print "USER:BACKEND:", user.backend
    print "REQUEST:USER:", request.user

    assert user.is_authenticated()

    request.session['start-data'] = start_data
    return http.HttpResponseRedirect('/client/tool/' + start_data['data']['exam'] + '/')


@csrf_exempt
def run_adding_test(request):
    # run exam..
    print "REQUEST:USER:", request.user
    print "REQUEST:POST:", request.POST
    return http.HttpResponse(u"""
    <!doctype html>
    <head>
    </head>
    <body>
        <form action="." method="POST">
            <pre>5 + 2 = 7</pre>
            <input type="submit" name=answer value="ja">
            <input type="submit" name=answer value="nei">
        </form>
    </body>
    </html>
    """)



def return_result_token(request):
    token = str(random.randrange(2**16, 2**32))

    start = request.session['start-data']['data']
    result = {
        'token': token,
        'type': 'result',
        'timestamp': datetime.datetime.now().isoformat(),
        'data': {
            'persnr': start['persnr'],
            'participant_id': 42,      # client-local ID
            'exam': start['exam'],  # (my-tool)
            'passed': True,         # did the user pass the test
            "score": 42,
            "system": start['system'],
            "exam_type": start["exam_kind"]  # historical accident..
        }
    }
    dkredis.set_pyval('CLIENT-TOKEN-' + token,
                      result,
                      200)  # seconds

    url = SERVER_ROOT_URL + RESULT_TOKEN_URL
    url += '?access_token=' + token
    url += '&client=testclient'  # must match Client.name
    print "REDIRECTING TO: ", url

    return http.HttpResponseRedirect(url)


def send_result_data(request):
    print "in send-result-data:", request.GET
    result = dkredis.pop_pyval("CLIENT-TOKEN-" + request.GET['access_token'])
    print "CLIENT_RESULT:", result
    return toolcall.message.SuccessResponse(
        result
    )
