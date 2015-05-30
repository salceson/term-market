from django.contrib import auth

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, RedirectView, ListView, DeleteView, UpdateView, View, CreateView
from requests_oauthlib import OAuth2Session
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.http import urlquote
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from json import dumps

from .models import Offer, Term, OfferWantedTerm
from term_market.forms import OfferCreateUpdateForm


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
    try:
        state = request.session['oauth_state']
    except KeyError:
        return redirect(settings.LOGIN_REDIRECT_URL)
    oauth = OAuth2Session(settings.OAUTH_CLIENT_ID,
                          redirect_uri=settings.OAUTH_REDIRECT_URI,
                          scope=settings.OAUTH_SCOPE,
                          state=state)
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


class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'term_market/term_list.html'

    def get_context_data(self, **kwargs):
        context_data = super(ScheduleView, self).get_context_data(**kwargs)
        object_list = []
        calendar_start = timezone.now()
        for term in self.request.user.terms.all():
            if calendar_start > term.start_time:
                calendar_start = term.start_time
            t = {
                'title': '%s - %s' % (term.subject, term.teacher),
                'start': term.start_time.isoformat(),
                'end': term.end_time.isoformat(),
                'url': reverse('offer_create', kwargs={'term_pk': term.pk}),
            }
            object_list.append(t)
        context_data['object_list'] = mark_safe(dumps(object_list))
        context_data['calendar_start'] = calendar_start.isoformat()
        return context_data


class OfferListView(LoginRequiredMixin, ListView):
    model = OfferWantedTerm
    template_name = 'term_market/offer_list.html'

    def get_queryset(self):
        return super(OfferListView, self).get_queryset().filter(term__in=self.request.user.terms.all()).order_by(
            'offer')


class MyOfferView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'term_market/my_offer_list.html'

    def get_queryset(self):
        return super(MyOfferView, self).get_queryset().filter(donor=self.request.user)


class MyOfferCreateView(LoginRequiredMixin, CreateView):
    model = Offer
    form_class = OfferCreateUpdateForm
    success_url = '/my_offers'

    def get_form_kwargs(self):
        kwargs = super(MyOfferCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['initial'] = {'offered_term': get_object_or_404(Term, pk=self.kwargs['term_pk'])}
        return kwargs


class MyOfferUpdateView(LoginRequiredMixin, UpdateView):
    model = Offer
    form_class = OfferCreateUpdateForm
    success_url = '/my_offers'

    def get_queryset(self):
        return super(MyOfferUpdateView, self).get_queryset().filter(donor=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(MyOfferUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MyOfferDeleteView(LoginRequiredMixin, DeleteView):
    model = Offer
    success_url = '/my_offers'

    def get_queryset(self):
        return super(MyOfferDeleteView, self).get_queryset().filter(donor=self.request.user)
