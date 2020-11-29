from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

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

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        resolved = get_status_resolved(id=1)
        resolution = cleaned_data.get('resolution')

        if not resolution and status == resolved:
            msg = forms.ValidationError('This field is required')
            self.add_error('resolution', msg)

class IncidentCrispyForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

        widgets = {
            #Change Active boolean checkbox to select
            #Set all fields to readonly (disabled)
            #'active' : forms.Select(choices=ACTIVE_CHOICES, attrs={'class' : 'selectpicker ', 'disabled':'disabled'}),
            'number' : forms.TextInput(attrs={'disabled':'disabled'}),
            'created' : forms.DateTimeInput(attrs={'disabled':'disabled'}, format='%m/%d/%Y %H:%M'),
            'updated' : forms.DateTimeInput(attrs={'disabled':'disabled'}, format='%m/%d/%Y %H:%M'),
            'resolved' : forms.DateTimeInput(attrs={'disabled':'disabled'}, format='%m/%d/%Y %H:%M'),
            'closed' : forms.DateTimeInput(attrs={'disabled':'disabled'}, format='%m/%d/%Y %H:%M'),
            #'status' : forms.Select(choices=status_choices(id=1), attrs={'class' : 'selectpicker '}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        #Add Save button
        #self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_method = 'POST'

        #Change form label names
        self.fields['desc_short'].label = 'Short Description'
        self.fields['desc_long'].label = 'Detailed Description'

        #Set values for status select field from database
        self.fields['status'].choices = status_choices(id=1)

        #Set form layout using bootsrap
        self.helper.layout = Layout(
            Submit('submit', "Submit From", css_class="btn"),
            Row(
                Column('number', css_class='form-group col-md-6 mb-0 readonly'),
                Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('customer', css_class='form-group col-md-6 mb-0'),
                Column('active', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('assignment_group', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('priority', css_class='form-group col-md-6 mb-0'),
                Column('assignee', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('location', css_class='form-group col-md-6 mb-0'),
                #Column('device_ci', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('created', css_class='form-group col-md-6 mb-0'),
                #Column('category', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('updated', css_class='form-group col-md-6 mb-0'),
                #Column('category_sub1', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('desc_short', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('desc_long', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('resolved', css_class='form-group col-md-6 mb-0'),
                Column('closed', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('resolution', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
        )
