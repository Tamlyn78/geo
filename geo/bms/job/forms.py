from django import forms
from django.forms import ModelForm

from .models import Job, Title, Status

class JobForm(ModelForm):
    note = forms.CharField(max_length=200)
    class Meta:
        model = Job
        fields = ['note',]

class TitleForm(ModelForm):
    title = forms.CharField(max_length=200)
    note = forms.CharField(max_length=200)
    class Meta:
        model = Title
        fields = ['id', 'title', 'note']

class StatusForm(ModelForm):
    note = forms.CharField(max_length=200)
    class Meta:
        model = Status
        fields = ['id', 'status', 'note']

