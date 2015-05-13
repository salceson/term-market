# coding=utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views.generic import TemplateView

from .forms import ImportForm



# TODO: Proper file handling
def handle_uploaded_file(f):
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
    context = {'title': 'Import'}

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, self.context, context_instance=RequestContext(request))
