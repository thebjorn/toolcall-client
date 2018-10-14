# -*- coding: utf-8 -*-
"""
This file contains the two views that a toolcall client needs to implement.
"""
import json
from django import http
from django.contrib.auth import login
from django.contrib.auth.models import User
import dkredis
from django.core.urlresolvers import reverse

from toolcall_client.apiutils import error_response
from . import apiutils, utils


def send_result_data(request):
    """This view runs when the toolcall server sends a result token, and returns
       the saved result data.
    """
    result = dkredis.pop_pyval("CLIENT-TOKEN-" + request.REQUEST['access_token'])
    r = http.HttpResponse(json.dumps(result, indent=4))
    r['Content-Type'] = 'application/json'
    return r


def receive_start_token(request):
    """This view runs when a user has been redirected with a start token.
       It will fetch the start_data and redirect the user to the correct tool.
    """

    token = apiutils.get_start_token(request)
    try:
        start_data = apiutils.fetch_start_data(token)
        # print "START-DATA:", json.dumps(start_data, indent=4)
    except apiutils.ToolCallError as toolerr:
        # display errors to user (with token) if you can't handle the error
        # in a reasonable fashion
        return error_response(toolerr)

    # Note: you have to return start_data['system'] with your result data.
    #       Here I log the user in and save it in their session, there are
    #       probably other/better ways to do this.

    username = utils.find_username(start_data)  # local username

    # create user if it's a new/unknown user
    if not User.objects.filter(username=username):
        request.user = User.objects.create_user(
            username=username,
            first_name=start_data['firstName'],
            last_name=start_data['lastName'],
        )

    # log the user in locally
    user = User.objects.get(username=username)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    # assert request.user.is_authenticated()

    # save the start data in the logged-in user's session
    request.session['start-data'] = start_data

    # redirect to the correct exam (the slug/exam field is set as the name in urls.py)
    return http.HttpResponseRedirect(reverse(start_data['exam']))
