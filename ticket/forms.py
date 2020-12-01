from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper

from .models import *
from .utils import *


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

        widgets = {
            
            #Set fields to readonly (disabled)
            'number' : forms.TextInput(attrs={'readonly':'readonly'}),
            'created' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'updated' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'resolved' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'reopened' : forms.TextInput(attrs={'readonly':'readonly'}),
            'closed' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            
            #Set 'active' boolean to a readonly textbox
            'active' : forms.TextInput(attrs={'readonly':'readonly'}),                
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        #self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_method = 'POST'

        #Change form label names
        self.fields['desc_short'].label = 'Short Description'
        self.fields['desc_long'].label = 'Detailed Description'
        self.fields['reopened'].label = 'Reopened Count'

        #Set values for status select fields from database
        self.fields['status'].choices = get_status_choices(id=1)
        self.fields['assignment_group'].choices = get_assignment_group_choices()

        #Set required fields
        self.fields['customer'].required = True
        self.fields['status'].required = True
        self.fields['priority'].required = True
        self.fields['assignment_group'].required = True

        #Remove select default (empty label) option
        self.fields['priority'].empty_label = None


