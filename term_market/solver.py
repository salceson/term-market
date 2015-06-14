# -*- coding: utf-8 -*-
from uuid import uuid4 as random_uuid
from os.path import dirname
import json

from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import Form
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from .models import Enrollment, Offer, Term
from .tasks import run_solver, task_check
from .views import PermissionRequiredMixin


def get_conflicts_for_enrollment(enrollment):
    conflicts = {}
    for term in Term.objects.filter(subject__enrollment=enrollment):
        term_conflicts = map(lambda c: c.id, list(term.conflicting_terms.all()))
        conflicts[str(term.id)] = term_conflicts
    return conflicts


def get_offers(enrollment):
    offers_list = []
    offers = Offer.objects.filter(offered_term__subject__enrollment=enrollment, is_available=True)
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
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        uuid = str(random_uuid())
        directory = settings.TEMP_DIR
        filename_prefix = dirname(directory) + '/' + uuid
        offers_file = filename_prefix + '_offers.json'
        conflicts_file = filename_prefix + '_conflicts.json'
        conflicts = get_conflicts_for_enrollment(enrollment)
        offers = get_offers(enrollment)
        with open(offers_file, 'w') as o:
            json.dump(offers, o)
        with open(conflicts_file, 'w') as c:
            json.dump(conflicts, c)
        output_file = filename_prefix + '_output.csv'
        result = run_solver.apply_async(args=(enrollment, offers_file, conflicts_file, output_file))
        self.task_id = str(result.task_id)
        return super(ManualSolverRunView, self).form_valid(form)

    def get_success_url(self):
        return reverse('solver_running', kwargs={'enrollment': self.kwargs['enrollment'], 'task': self.task_id})


class ManualSolverRunningView(PermissionRequiredMixin, TemplateView):
    template_name = "term_market/admin/solver_running.html"
    object = Enrollment
    permission_required = 'term_market.change_enrollment'

    def get_context_data(self, **kwargs):
        context = super(ManualSolverRunningView, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        task = self.kwargs['task']
        context.update({'title': 'Run solver', 'enrollment_name': enrollment.name, 'task': task})
        return context


@permission_required("term_market.change_enrollment")
def solver_task_check(request, task=None):
    return task_check(task, 'Unexpected error occurred during running solver!')
