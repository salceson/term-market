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
import notifications

from django.conf.urls import include, url
from django.contrib import admin

from term_market.views import IndexView, LoginView, LogoutView, ScheduleView, OfferListView, MyOfferView, \
    MyOfferDeleteView, MyOfferUpdateView, MyOfferCreateView, TermOfferAcceptView
from term_market.import_export import ImportTerms, ImportTermsSuccess, ImportDepartmentListSuccess, \
    ImportDepartmentList, ImportConflicts, ImportConflictsSuccess, Export


urlpatterns = [
    url(r'^djangojs/', include('djangojs.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/import/terms/$',
        ImportTerms.as_view(), name='import_terms'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/import/terms/success/(?P<task>[a-zA-Z0-9\-]+)/$',
        ImportTermsSuccess.as_view(), name='import_terms_success'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/import/department-list/$',
        ImportDepartmentList.as_view(), name='import_department_list'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)'
        r'/import/department-list/success/(?P<task>[a-zA-Z0-9\-]+)/$',
        ImportDepartmentListSuccess.as_view(), name='import_department_list_success'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/import/conflicts/$',
        ImportConflicts.as_view(), name='import_conflicts'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)'
        r'/import/conflicts/success/(?P<task>[a-zA-Z0-9\-]+)/$',
        ImportConflictsSuccess.as_view(), name='import_conflicts_success'),
    url(r'^admin/term_market/enrollment/import/check/(?P<task>[a-zA-Z0-9\-]+)/$',
        'term_market.import_export.import_check', name='import_check'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/export/$',
        Export.as_view(), name='export'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/export/download/$',
        'term_market.import_export.export_data', name='export_download'),
    url(r'^admin/term_market/enrollment/(?P<enrollment>[0-9]+)/solver/export/download/$',
        'term_market.solver.export_solver_data', name='solver_export_download'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^schedule/$', ScheduleView.as_view(), name='schedule'),
    url(r'^my_offers/$', MyOfferView.as_view(), name='my_offers'),
    url(r'^offers/add/term-(?P<term_pk>[0-9]+)$', MyOfferCreateView.as_view(), name='offer_create'),
    url(r'^offers/(?P<pk>[0-9]+)/delete$', MyOfferDeleteView.as_view(), name='offer_delete'),
    url(r'^offers/(?P<pk>[0-9]+)/update$', MyOfferUpdateView.as_view(), name='offer_update'),
    url(r'^offers/$', OfferListView.as_view(), name='offers'),
    url(r'^term_offer/(?P<pk>[0-9]+)/accept$', TermOfferAcceptView.as_view(), name='term_offer_accept'),
    url(r'^accounts/login/$', LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/oauth-callback/$', 'term_market.views.oauth_callback', name='oauth_callback'),
    url(r'^notifications/', include(notifications.urls), name='notifications'),
]
