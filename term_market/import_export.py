# coding=utf-8

import hashlib
import time
from os.path import dirname

from django.http import JsonResponse
from django.shortcuts import render

from .forms import ImportTermsForm
from .tasks import import_terms_task


def handle_uploaded_file(f, suffix):
    time_hash = hashlib.sha1()
    time_hash.update(str(time.time()))
    # directory = settings.TEMP_DIR
    directory = '/tmp/'
    filename = dirname(directory) + '/' + time_hash.hexdigest() + suffix
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    return filename


def import_terms(request):
    context = {'title': 'Import terms'}
    if request.method == 'POST':
        form = ImportTermsForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES['file'], '_terms.txt')
            result = import_terms_task.apply_async(args=(filename, form.cleaned_data['enrollment']))
            task_id = result.task_id
            context.update({'task': str(task_id)})
            return render(request, 'term_market/admin/import_success.html', context)
    else:
        form = ImportTermsForm()
    context.update({'form': form})
    return render(request, 'term_market/admin/import_terms.html', context)


def import_check(_, task=None):
    if not task:
        return JsonResponse(
            {'status': 'error', 'msg': 'Wrong task id'}
        )
    try:
        task_result = import_terms_task.AsyncResult(task)
    except:
        return JsonResponse(
            {'status': 'error', 'msg': 'Wrong task id'}
        )
    finished = task_result.ready()
    success = False if not finished else task_result.get()
    return JsonResponse(
        {'status': 'ok', 'finished': finished, 'success': success}
    )
