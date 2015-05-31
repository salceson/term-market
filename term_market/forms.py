# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django import forms
from django.forms import ModelForm

from term_market.models import Offer, Term
from term_market.utils import instance_as_queryset


class ImportTermsForm(forms.Form):
    file = forms.FileField(label="Terms file")


class ImportDepartmentListForm(forms.Form):
    file = forms.FileField(label="Department list file")


class ImportConflictsForm(forms.Form):
    file = forms.FileField(label="Conflicts file")


class OfferCreateUpdateForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(OfferCreateUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.user = user

        if kwargs.get('instance'):
            button = Submit('update', 'Update offer')
            self.offered_term = kwargs['instance'].offered_term
        else:
            button = Submit('create', 'Create offer')
            self.offered_term = kwargs['initial']['offered_term']

        self.fields['offered_term'].queryset = instance_as_queryset(self.offered_term)

        subjects = self.user.terms.values_list('subject').distinct()
        self.fields['wanted_terms'].queryset = Term.objects.filter(subject__in=subjects)

        self.helper.layout = Layout(
            Field('offered_term'),
            Field('wanted_terms', size='8'),
            'bait',
            button
        )

    def save(self, *args, **kwargs):
        self.instance.donor = self.user
        self.instance.offered_term = self.offered_term
        return super(OfferCreateUpdateForm, self).save(*args, **kwargs)

    class Meta:
        model = Offer
        fields = ['offered_term', 'wanted_terms', 'bait']