from django import forms
from django.forms import ModelForm

from .models import *


class AttachmentForm(forms.ModelForm):

    class Meta:
        model = Attachment
        fields = ['document']

