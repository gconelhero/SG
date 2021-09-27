# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views, ajax_views

from djangosige.configs import DEBUG

app_name = 'base'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'setcache/', ajax_views.setCache.as_view(), name='setcache'),
]

if DEBUG:
    urlpatterns += [
        url(r'^404/$', views.handler404),
        url(r'^500/$', views.handler500),
    ]
