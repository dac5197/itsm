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
            'closed' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'created' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'created_by' : forms.TextInput(attrs={'readonly':'readonly'}),
            'reopened' : forms.TextInput(attrs={'readonly':'readonly'}),
            'resolved' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'updated' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            
            #Set 'active' boolean to a readonly textbox
            'active' : forms.TextInput(attrs={'readonly':'readonly'}),                
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        #Change form label names
        self.fields['desc_short'].label = 'Short Description'
        self.fields['desc_long'].label = 'Detailed Description'
        self.fields['reopened'].label = 'Reopened Count'

        #Set values for status select fields from database
        self.fields['status'].choices = get_status_choices(id=1)
        self.fields['priority'].choices = get_priority_choices()
        self.fields['assignment_group'].choices = get_assignment_group_choices()

        #Set required fields
        self.fields['customer'].required = True
        self.fields['status'].required = True
        self.fields['priority'].required = True
        self.fields['assignment_group'].required = True

        #Set not required fields
        self.fields['assignee'].required = False

        #Remove select default (empty label) option
        self.fields['priority'].empty_label = None


        #Clear values for the assignee select
        self.fields['assignee'].queryset = Customer.objects.none()

        #Set values for the assignee select:
        #   If POST, get assignment group ID from request data
        #   Else, get assignment group ID from form instance
        #Get group membership and populated assignee select
        #https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
        if 'assignment_group' in self.data:
            try:
                assignment_group_id = int(self.data.get('assignment_group'))
                grp = ITSMGroup.objects.get(id=assignment_group_id)
                self.fields['assignee'].queryset = Customer.objects.filter(itsm_group_membership=grp).order_by('last_name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            assignment_group = self.instance.assignment_group
            if assignment_group:
                grp = ITSMGroup.objects.get(id=assignment_group.id)
                self.fields['assignee'].queryset = Customer.objects.filter(itsm_group_membership=grp).order_by('last_name')
            else:
                self.fields['assignment_group'].initial = '---------'

    #On form save, if status is resolved and resolution is empty, then throw error
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        resolution = cleaned_data.get("resolution")

        resolved_status = get_status_resolved(id=1)

        if status == resolved_status and resolution == '':
            msg = "This field is required when resolving an incident."
            self.add_error('resolution', msg)

        return self.cleaned_data
        #return cleaned_data            

class IncidentSearchForm(IncidentForm):
    class Meta:
        model = Incident
        exclude = ['sysID']

