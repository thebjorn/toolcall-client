# -*- coding: utf-8 -*-

""":mod:`toolcall.toolimplementor` urls.
"""

from django.conf.urls import *  # pylint:disable=W0401
from . import views

urlpatterns = [
    # api urls (must match urls set in Client model)
    url(r'^start-tool/$', views.receive_start_token),
    url(r'^result/$', views.send_result_data),

    # demonstration url
    url(r'^tool/adding-test/$', views.run_adding_test),
    # url(r'^tool/(?P<slug>[-\w\d]+)/$', views.run_tool),
]
