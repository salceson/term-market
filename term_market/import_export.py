# -*- coding: utf-8 -*-

from uuid import uuid4 as random_uuid
from os.path import dirname

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import OperationalError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from .forms import ImportTermsForm, ImportDepartmentListForm
from .tasks import import_terms_task, import_department_list_task
from .models import Enrollment
from term_market.views import LoginRequiredMixin, PermissionRequiredMixin


def handle_uploaded_file(f, suffix):
    directory = settings.TEMP_DIR
    filename = dirname(directory) + '/' + str(random_uuid()) + suffix
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    return filename


class Import(FormView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = 'term_market.change_enrollment'
    object = Enrollment

    def __init__(self, success_link_name, task, suffix, title, **kwargs):
        super(Import, self).__init__(**kwargs)
        self.success_link_name = success_link_name
        self.task = task
        self.suffix = suffix
        self.title = title

    def get_context_data(self, **kwargs):
        context = super(Import, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        context.update({'title': self.title, 'enrollment_name': enrollment.name})
        return context

    def form_valid(self, form):
        filename = handle_uploaded_file(self.request.FILES['file'], self.suffix)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        result = self.task.apply_async(args=(filename, enrollment))
        self.task_id = str(result.task_id)
        return super(Import, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_link_name, kwargs={'enrollment': self.kwargs['enrollment'], 'task': self.task_id})


class ImportTerms(Import):
    form_class = ImportTermsForm
    template_name = "term_market/admin/import_terms.html"

    def __init__(self, **kwargs):
        super(ImportTerms, self).__init__('import_terms_success', import_terms_task, '_terms.txt', 'Import terms',
                                          **kwargs)


class ImportDepartmentList(Import):
    form_class = ImportDepartmentListForm
    template_name = "term_market/admin/import_department_list.html"

    def __init__(self, **kwargs):
        super(ImportDepartmentList, self).__init__('import_department_list_success', import_department_list_task,
                                                   '_department_list.txt', 'Import department list', **kwargs)


class ImportSuccess(TemplateView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = 'term_market.change_enrollment'
    object = Enrollment
    template_name = 'term_market/admin/import_success.html'

    def __init__(self, title, **kwargs):
        super(ImportSuccess, self).__init__(**kwargs)
        self.title = title

    def get_context_data(self, **kwargs):
        context = super(ImportSuccess, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        task_id = self.kwargs['task']
        context.update({'title': self.title, 'enrollment_name': enrollment.name, 'task': task_id})
        return context


class ImportTermsSuccess(ImportSuccess):
    def __init__(self, **kwargs):
        super(ImportTermsSuccess, self).__init__('Import terms', **kwargs)


class ImportDepartmentListSuccess(ImportSuccess):
    def __init__(self, **kwargs):
        super(ImportDepartmentListSuccess, self).__init__('Import department list', **kwargs)


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
