from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import Form, ModelForm

from crispy_forms.helper import FormHelper

from .models import *
from .utils import get_all_customer_choices, get_all_group_choices

class CustomerForm(forms.ModelForm):
    profile_image = forms.ImageField(label='Profile Image',required=False, error_messages ={'invalid': "Image files only"}, widget=forms.FileInput)

    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user', 'sysID']

        widgets = {     
            #Set fields to readonly (disabled)
            'created' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'updated' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),           
        }


class CustomerRegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['sysID']


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        #Change form label names
        self.fields['password2'].label = 'Confirm Password'


class GroupForm(forms.ModelForm):
    class Meta:
        model = ITSMGroup
        fields = ['members']


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = ITSMGroup
        fields = '__all__'
        exclude = ['permissions', 'sysID']

        widgets = {     
            #Set fields to readonly (disabled)
            'created' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'updated' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),           
        }


class GroupCascadeRolesForm(forms.Form):
    tsm_group = forms.ChoiceField(choices=get_all_group_choices())