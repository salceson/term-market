"""TermMarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from term_market.views import IndexView, LoginView, LogoutView, ScheduleView, OfferListView, MyOfferView, \
    MyOfferDeleteView, MyOfferUpdateView

urlpatterns = [
    url(r'^djangojs/', include('djangojs.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^schedule/$', ScheduleView.as_view(), name='schedule'),
    url(r'^my_offers/$', MyOfferView.as_view(), name='my_offers'),
    url(r'^offers/(?P<pk>[0-9]+)/delete$', MyOfferDeleteView.as_view(), name='offer_delete'),
    url(r'^offers/(?P<pk>[0-9]+)/update$', MyOfferUpdateView.as_view(), name='offer_update'),
    url(r'^offers/$', OfferListView.as_view(), name='offers'),
    url(r'^accounts/login/$', LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/oauth-callback/$', 'term_market.views.oauth_callback', name='oauth_callback'),
]
