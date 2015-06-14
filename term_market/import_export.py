# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from itertools import groupby
from operator import attrgetter

from uuid import uuid4 as random_uuid
from os.path import dirname

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import permission_required

from .forms import ImportTermsForm, ImportDepartmentListForm, ImportConflictsForm
from .tasks import import_terms_task, import_department_list_task, import_conflicts_task, delete_file, task_check
from .models import Enrollment, Term, TermStudent
from .views import PermissionRequiredMixin


def handle_uploaded_file(f, suffix):
    directory = settings.TEMP_DIR
    filename = dirname(directory) + '/' + str(random_uuid()) + suffix
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    return filename


class Import(PermissionRequiredMixin, FormView):
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


class ImportConflicts(Import):
    form_class = ImportConflictsForm
    template_name = "term_market/admin/import_conflicts.html"

    def __init__(self, **kwargs):
        super(ImportConflicts, self).__init__('import_conflicts_success', import_conflicts_task, '_conflicts.txt',
                                              'Import conflicts', **kwargs)


class ImportSuccess(PermissionRequiredMixin, TemplateView):
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


class ImportConflictsSuccess(ImportSuccess):
    def __init__(self, **kwargs):
        super(ImportConflictsSuccess, self).__init__('Import conflicts', **kwargs)


class Export(PermissionRequiredMixin, TemplateView):
    permission_required = 'term_market.change_enrollment'
    object = Enrollment
    template_name = 'term_market/admin/export.html'

    def get_context_data(self, **kwargs):
        context = super(Export, self).get_context_data(**kwargs)
        enrollment = get_object_or_404(Enrollment, id=self.kwargs['enrollment'])
        context.update({'title': 'Export enrollment data', 'enrollment_name': enrollment.name,
                        'enrollment_id': enrollment.id})
        return context


@permission_required("term_market.change_enrollment")
def export_data(request, enrollment=None):
    enrollment = get_object_or_404(Enrollment, id=enrollment)
    terms = Term.objects.filter(subject__enrollment=enrollment)
    mapping = TermStudent.objects.filter(term__in=terms).select_related('term', 'term__subject').order_by(
        'user', 'term__subject')
    filename = settings.TEMP_DIR + str(random_uuid()) + '_export.csv'
    with open(filename, 'w') as f:
        for student, assignments in groupby(mapping, attrgetter('user')):
            f.write('[%s]\n' % student.transcript_no)
            for assignment in assignments:
                f.write('%d:%d\n' % (assignment.term.subject.external_id, assignment.term.external_id))
    response = HttpResponse(FileWrapper(open(filename)), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    delete_file.apply_async(countdown=120, args=[filename])
    return response


@permission_required("term_market.change_enrollment")
def import_task_check(request, task=None):
    return task_check(task, 'Unexpected error occurred during import. It may be possible that your'
                            ' file is not in correct format!')
