# -*- coding: utf-8 -*-
from uuid import uuid4 as random_uuid

from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import Form
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from .models import Enrollment, Offer, Term
from .views import PermissionRequiredMixin


@permission_required("term_market.change_enrollment")
def export_solver_data(request, enrollment=None):
    uuid = str(random_uuid())
    print uuid
    enrollment = get_object_or_404(Enrollment, id=enrollment)
    conflicts = get_conflicts_for_enrollment(enrollment)
    print conflicts
    offers = get_offers(enrollment)
    print offers
    return JsonResponse({"conflicts": conflicts, "offers": offers})


def get_conflicts_for_enrollment(enrollment):
    conflicts = {}
    for term in Term.objects.filter(subject__enrollment=enrollment):
        term_conflicts = map(lambda c: c.id, list(term.conflicting_terms.all()))
        conflicts[str(term.id)] = term_conflicts
    return conflicts


def get_offers(enrollment):
    offers_list = []
    offers = Offer.objects.filter(offered_term__subject__enrollment=enrollment)
    for offer in offers:
        offers_list.append({
            "id": offer.id,
            "donor": offer.donor.id,
            "offered_term": offer.offered_term.id,
            "wanted_terms": map(lambda o: o.id, offer.wanted_terms.all())
        })
    return {"offers": offers_list}


class ManualSolverRunView(PermissionRequiredMixin, FormView):
    template_name = "term_market/admin/solver_run.html"
    object = Enrollment
    permission_required = 'term_market.change_enrollment'
    form_class = Form

    def get_context_data(self, **kwargs):
        context = super(ManualSolverRunView, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        context.update({'title': 'Run solver', 'enrollment_name': enrollment.name})
        return context

    def form_valid(self, form):
        # TODO: Proper actions here (running the solver)
        return super(ManualSolverRunView, self).form_valid(form)

    def get_success_url(self):
        return reverse('solver_running', kwargs={'enrollment': self.kwargs['enrollment']})


class ManualSolverRunningView(PermissionRequiredMixin, TemplateView):
    template_name = "term_market/admin/solver_running.html"
    object = Enrollment
    permission_required = 'term_market.change_enrollment'

    def get_context_data(self, **kwargs):
        context = super(ManualSolverRunningView, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        context.update({'title': 'Run solver', 'enrollment_name': enrollment.name})
        return context
