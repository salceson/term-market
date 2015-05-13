# coding=utf-8

import hashlib
import os
import time
from os.path import dirname

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.views.generic import TemplateView
from django.conf import settings

from .forms import ImportForm


def handle_uploaded_file(f):
    time_hash = hashlib.sha1()
    time_hash.update(str(time.time()))
    directory = settings.TEMP_DIR
    filename = dirname(directory) + '/' + time_hash.hexdigest() + '_terms.txt'
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    # TODO: Proper file handling
    os.remove(filename)


def import_terms(request):
    params = {}
    params.update(csrf(request))
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/admin/import/success')
    else:
        form = ImportForm()
    params.update({'form': form, 'title': 'Import'})
    return render_to_response('term_market/admin/import.html', params)


class ImportSuccessful(TemplateView):
    template_name = "term_market/admin/import_success.html"

    def get_context_data(self, **kwargs):
        context = super(ImportSuccessful, self).get_context_data(**kwargs)
        context.update({u'title': u'Import'})
        return context
