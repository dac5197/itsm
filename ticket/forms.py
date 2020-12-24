from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper

from .models import *
from .utils import *


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

        widgets = set_ticket_form_widgets(completion_field_name='resolved')

    #Set form field labels, select choices, and required attribute
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self = set_ticket_form_defaults(form=self, ticket_type_id=1)

    #On form save, if status is resolved and resolution is empty, then throw error
    def clean(self):
        cleaned_data = super().clean()
        self = validate_completion_fields(form=self, cleaned_data=cleaned_data, completion_field='resolved', ticket_type_id=1)

        return self.cleaned_data
         

class IncidentSearchForm(IncidentForm):
    class Meta:
        model = Incident
        exclude = ['sysID']


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'

        widgets = set_ticket_form_widgets(completion_field_name='fulfilled')

    #Set form field labels, select choices, and required attribute
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self = set_ticket_form_defaults(form=self, ticket_type_id=2)

    #On form save, if status is resolved and resolution is empty, then throw error
    def clean(self):
        cleaned_data = super().clean()
        self = validate_completion_fields(form=self, cleaned_data=cleaned_data, completion_field='fulfillment_notes', ticket_type_id=2)

        return self.cleaned_data
           

class RequestSearchForm(IncidentForm):
    class Meta:
        model = Incident
        exclude = ['sysID']
