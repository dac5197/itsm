from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import Form, ModelForm

from crispy_forms.helper import FormHelper

from .models import *

class CustomerForm(forms.ModelForm):
    profile_image = forms.ImageField(label='Profile Image',required=False, error_messages ={'invalid': "Image files only"}, widget=forms.FileInput)

    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user', 'sysID']


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

class GroupForm(forms.Form):
    tsm_group = forms.ChoiceField(choices=[(group.id, group.name) for group in ITSMGroup.objects.all().order_by('path')])