# coding=utf-8

import hashlib
import os
import time
from os.path import dirname

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

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
    if request.method == 'POST':
        form = ImportTermsForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES['file'], '_terms.txt')
            result = import_terms_task.apply_async(args=(filename, form.cleaned_data['enrollment']))
            print result
            os.remove(filename)
            return HttpResponseRedirect('/admin/import/success/')
    else:
        form = ImportTermsForm()
    context = {'form': form, 'title': 'Import terms'}
    return render(request, 'term_market/admin/import_terms.html', context)


class ImportSuccessful(TemplateView):
    template_name = "term_market/admin/import_success.html"

    def get_context_data(self, **kwargs):
        context = super(ImportSuccessful, self).get_context_data(**kwargs)
        context.update({'title': 'Import terms'})
        return context
