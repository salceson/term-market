# -*- coding: utf-8 -*-

from uuid import uuid4 as random_uuid
from os.path import dirname

from django.conf import settings
from django.db import OperationalError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

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


def import_terms(request, enrollment=None):
    context = {'title': 'Import terms'}
    enrollment = get_object_or_404(Enrollment, id=enrollment)
    context.update({'enrollment_name': enrollment.name})
    if request.method == 'POST':
        form = ImportTermsForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES['file'], '_terms.txt')
            result = import_terms_task.apply_async(args=(filename, enrollment))
            task_id = result.task_id
            context.update({'task': str(task_id)})
            return render(request, 'term_market/admin/import_success.html', context)
    else:
        form = ImportTermsForm()
    context.update({'form': form})
    return render(request, 'term_market/admin/import_terms.html', context)


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
    elif finished:
        success = False
        message = 'Unexpected error occured during import. It may be possible that your file is not in correct format!'
    else:
        success = False
        message = ''
    message = message.replace('<', '&lt;')
    message = message.replace('>', '&gt;')
    return JsonResponse(
        {'status': 'ok', 'finished': finished, 'success': success, 'message': message}
    )
