from django import forms

from .models import Enrollment


class ImportForm(forms.Form):
    enrollment = forms.ModelChoiceField(queryset=Enrollment.objects, empty_label="(Select Enrollment)",
                                        label="Enrollment")
    file = forms.FileField(label="Terms file")