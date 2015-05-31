# coding=utf-8
from django.contrib import auth, messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import F
from django.shortcuts import redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, RedirectView, ListView, DeleteView, UpdateView, CreateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
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


class AvailableOffersMixin(object):
    def get_queryset(self):
        qs = super(AvailableOffersMixin, self).get_queryset()
        qs = qs.filter(term__subject=F('offer__offered_term__subject'), term__in=self.request.user.terms.all())
        qs = qs.exclude(offer__donor=self.request.user)
        qs = qs.exclude(offer__offered_term__in=self.request.user.terms.values_list('conflicting_terms', flat=True))
        qs = qs.order_by('offer')
        return qs


class MyOffersMixin(object):
    def get_queryset(self):
        qs = super(MyOffersMixin, self).get_queryset()
        qs = qs.filter(donor=self.request.user)
        return qs


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


class OfferListView(LoginRequiredMixin, AvailableOffersMixin, ListView):
    model = OfferWantedTerm
    template_name = 'term_market/offer_list.html'


class MyOfferView(LoginRequiredMixin, MyOffersMixin, ListView):
    model = Offer
    template_name = 'term_market/my_offer_list.html'


class MyOfferCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Offer
    form_class = OfferCreateUpdateForm
    success_url = reverse_lazy('my_offers')
    success_message = 'Offer created successfully'

    def get_form_kwargs(self):
        kwargs = super(MyOfferCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['initial'] = {'offered_term': get_object_or_404(self.request.user.terms, pk=self.kwargs['term_pk'])}
        return kwargs


class MyOfferUpdateView(LoginRequiredMixin, MyOffersMixin, SuccessMessageMixin, UpdateView):
    model = Offer
    form_class = OfferCreateUpdateForm
    success_url = reverse_lazy('my_offers')
    success_message = 'Offer updated successfully'

    def get_form_kwargs(self):
        kwargs = super(MyOfferUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MyOfferDeleteView(LoginRequiredMixin, MyOffersMixin, DeleteView):
    model = Offer
    success_url = reverse_lazy('my_offers')


class TermOfferAcceptView(LoginRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView, AvailableOffersMixin):
    model = OfferWantedTerm
    success_url = reverse_lazy('offers')
    template_name_suffix = '_confirm_accept'
    success_message = 'Offer accepted successfully'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.trade_to(self.request.user)
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    # This is to mimic "generic" behavior of Django built-in views
    # We may end up creating generic confirmation mixin.
    def get_success_url(self):
        return self.success_url
