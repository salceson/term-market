from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView, RedirectView, ListView, DeleteView, UpdateView
from requests_oauthlib import OAuth2Session

from .models import Offer


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


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


class ScheduleView(ListView):
    def get_queryset(self):
        return self.request.user.terms.all()


class OfferListView(ListView):
    model = Offer

    def get_queryset(self):
        return super(OfferListView, self).get_queryset().exclude(donor=self.request.user)


class MyOfferView(ListView):
    model = Offer
    template_name = 'term_market/my_offer_list.html'

    def get_queryset(self):
        return super(MyOfferView, self).get_queryset().filter(donor=self.request.user)


class MyOfferDeleteView(DeleteView):
    model = Offer
    success_url = '/my_offers'

    def get_queryset(self):
        return super(MyOfferDeleteView, self).get_queryset().filter(donor=self.request.user)


class MyOfferUpdateView(UpdateView):
    model = Offer
    fields = ['offered_term', 'wanted_terms', 'bait']
    template_name_suffix = '_update_form'
    success_url = '/my_offers'

    def get_queryset(self):
        return super(MyOfferUpdateView, self).get_queryset().filter(donor=self.request.user)