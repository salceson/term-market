# coding=utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context_processors import csrf

__author__ = 'Michał Ciołczyk'

from django import forms
from .models import Enrollment


class ImportForm(forms.Form):
    enrollment = forms.ModelChoiceField(queryset=Enrollment.objects, empty_label="(Select Enrollment)",
                                        label="Enrollment")
    termsFile = forms.FileField(label="Terms file")


def handle_uploaded_file(f):
    pass


def import_terms(request):
    params = {}
    params.update(csrf(request))
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['termsFile'])
            return HttpResponseRedirect('/admin/import/success')
    else:
        form = ImportForm()
    params.update({'form': form})
    return render_to_response('term_market/import.html', params)


def import_success(_):
    return render_to_response('term_market/import_success.html')