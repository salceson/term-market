# -*- coding: utf-8 -*-

from django import forms


class ImportTermsForm(forms.Form):
    file = forms.FileField(label="Terms file")