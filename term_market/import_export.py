# -*- coding: utf-8 -*-

from uuid import uuid4 as random_uuid
from os.path import dirname

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import OperationalError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from .forms import ImportTermsForm
from .tasks import import_terms_task
from .models import Enrollment


def handle_uploaded_file(f, suffix):
    directory = settings.TEMP_DIR
    filename = dirname(directory) + '/' + str(random_uuid()) + suffix
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    return filename


class ImportTerms(FormView):
    form_class = ImportTermsForm
    template_name = "term_market/admin/import_terms.html"

    def get_context_data(self, **kwargs):
        context = super(ImportTerms, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        context.update({'title': 'Import terms', 'enrollment_name': enrollment.name})
        return context

    def form_valid(self, form):
        filename = handle_uploaded_file(self.request.FILES['file'], "_terms.txt")
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        result = import_terms_task.apply_async(args=(filename, enrollment))
        self.task_id = str(result.task_id)
        return super(ImportTerms, self).form_valid(form)

    def get_success_url(self):
        return reverse('import_terms_success', kwargs={'enrollment': self.kwargs['enrollment'], 'task': self.task_id})


class ImportTermsSuccess(TemplateView):
    template_name = 'term_market/admin/import_terms_success.html'

    def get_context_data(self, **kwargs):
        context = super(ImportTermsSuccess, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        task_id = self.kwargs['task']
        context.update({'title': 'Import terms', 'enrollment_name': enrollment.name, 'task': task_id})
        return context


def import_check(request, task=None):
    if not task:
        return JsonResponse(
            {'status': 'error', 'msg': 'Wrong task id'}
        )
    task_result = None
    try:
        task_result = import_terms_task.AsyncResult(task)
        finished = task_result.ready()
    except OperationalError:
        finished = False
    if finished and task_result.status == 'SUCCESS':
        success, message = task_result.get()
    else:
        success = False
        message = 'Unexpected error occurred during import. It may be possible that your' \
                  ' file is not in correct format!' if finished else ''
    return JsonResponse(
        {'status': 'ok', 'finished': finished, 'success': success, 'message': message}
    )
