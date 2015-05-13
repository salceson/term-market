# coding=utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.views.generic import TemplateView

from .forms import ImportForm


def handle_uploaded_file(f):
    # TODO: Proper file handling
    with open('/tmp/dupa.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


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
    return render_to_response('term_market/import.html', params)


class ImportSuccessful(TemplateView):
    template_name = "term_market/import_success.html"

    def get_context_data(self, **kwargs):
        context = super(ImportSuccessful, self).get_context_data(**kwargs)
        context.update({u'title': u'Import'})
        return context
