from django.contrib import auth

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView, RedirectView, ListView, DeleteView, UpdateView
from requests_oauthlib import OAuth2Session
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.http import urlquote
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required

from .models import Offer


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class PermissionRequiredMixin(object):
    """
    Code from: https://github.com/lukaszb/django-guardian/issues/48
    """
    login_url = settings.LOGIN_URL
    raise_exception = False
    permission_required = None
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        original_return_value = super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)

        if self.permission_required is None or len(self.permission_required.split('.')) != 2:
            raise ImproperlyConfigured("'PermissionRequiredMixin' requires 'permission_required' attribute to be"
                                       " set to '<app_label>.<permission codename>' but is set to '%s' instead"
                                       % self.permission_required)

        if hasattr(self, 'object') and self.object is not None:
            has_permission = request.user.has_perm(self.permission_required, self.object)
        elif hasattr(self, 'get_object') and callable(self.get_object):
            has_permission = request.user.has_perm(self.permission_required, self.get_object())
        else:
            has_permission = request.user.has_perm(self.permission_required)

        if not has_permission:
            if self.raise_exception:
                return HttpResponseForbidden()
            else:
                path = urlquote(request.get_full_path())
                tup = self.login_url, self.redirect_field_name, path
                return HttpResponseRedirect("%s?%s=%s" % tup)
        return original_return_value


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'term_market/index.html'


class LoginView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        oauth = OAuth2Session(settings.OAUTH_CLIENT_ID,
                              redirect_uri=settings.OAUTH_REDIRECT_URI,
                              scope=settings.OAUTH_SCOPE)
        authorization_url, state = oauth.authorization_url(settings.OAUTH_AUTHORIZATION_URI)
        self.request.session['oauth_state'] = state
        return authorization_url


class LogoutView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        auth.logout(self.request)
        return settings.OAUTH_LOGOUT_URI


def oauth_callback(request):
    oauth = OAuth2Session(settings.OAUTH_CLIENT_ID,
                          redirect_uri=settings.OAUTH_REDIRECT_URI,
                          scope=settings.OAUTH_SCOPE,
                          state=request.session['oauth_state'])
    del request.session['oauth_state']
    authorization_response = request.build_absolute_uri()
    oauth.fetch_token(settings.OAUTH_TOKEN_URI,
                      authorization_response=authorization_response,
                      client_secret=settings.OAUTH_CLIENT_SECRET)
    user = auth.authenticate(oauth=oauth)
    if user:
        request.user = user
        auth.login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)
    raise PermissionDenied('Not authenticated')


class ScheduleView(ListView, LoginRequiredMixin):
    def get_queryset(self):
        return self.request.user.terms.all()


class OfferListView(ListView, LoginRequiredMixin):
    model = Offer

    def get_queryset(self):
        return super(OfferListView, self).get_queryset().exclude(donor=self.request.user)


class MyOfferView(ListView, LoginRequiredMixin):
    model = Offer
    template_name = 'term_market/my_offer_list.html'

    def get_queryset(self):
        return super(MyOfferView, self).get_queryset().filter(donor=self.request.user)


class MyOfferDeleteView(DeleteView, LoginRequiredMixin):
    model = Offer
    success_url = '/my_offers'

    def get_queryset(self):
        return super(MyOfferDeleteView, self).get_queryset().filter(donor=self.request.user)


class MyOfferUpdateView(UpdateView, LoginRequiredMixin):
    model = Offer
    fields = ['offered_term', 'wanted_terms', 'bait']
    template_name_suffix = '_update_form'
    success_url = '/my_offers'

    def get_queryset(self):
        return super(MyOfferUpdateView, self).get_queryset().filter(donor=self.request.user)