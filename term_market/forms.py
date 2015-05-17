# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

from django import forms
from django.forms import ModelForm
from term_market.models import Offer


class ImportTermsForm(forms.Form):
    file = forms.FileField(label="Terms file")


class ImportDepartmentListForm(forms.Form):
    file = forms.FileField(label="Department list file")


class OfferCreateUpdateForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(OfferCreateUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.fields['offered_term'].queryset = user.terms

        if kwargs.get('instance'):
            button = Submit('update', 'Update offer')
        else:
            button = Submit('create', 'Create offer')

        self.helper.layout = Layout(
            'offered_term',
            Field('wanted_terms', size='8'),
            'bait',
            button
        )

    class Meta:
        model = Offer
        fields = ['offered_term', 'wanted_terms', 'bait']