from django import forms

from .models import Enrollment


class ImportTermsForm(forms.Form):
    enrollment = forms.ModelChoiceField(queryset=Enrollment.objects, empty_label="(Select Enrollment)",
                                        label="Enrollment")
    file = forms.FileField(label="Terms file")