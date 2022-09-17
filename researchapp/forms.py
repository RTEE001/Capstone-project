from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from researchapp.models import Groups

from django.forms import ModelForm

from django import forms
       


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class GroupForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ('Gname',)
    