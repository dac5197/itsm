from django import forms
from django.forms import ModelForm

from .models import *

class WorkNoteForm(forms.ModelForm):
    class Meta:
        model = WorkNote
        fields = '__all__'