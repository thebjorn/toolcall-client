# -*- coding: utf-8 -*-

""":mod:`toolcall.toolimplementor` urls.
"""

from django.conf.urls import *  # pylint:disable=W0401

from . import views, exams

urlpatterns = [
    # api urls (these urls must match urls set in Client model)
    url(r'^start-tool/$', views.receive_start_token),
    url(r'^result/$', views.send_result_data),

    # the exam urls (you can e.g. set the name to the slug value from the tool definition)
    url(r'^tool/adding-test/$', exams.run_adding_test, name='adding-test'),
]
