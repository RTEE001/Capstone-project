from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm

from django import forms

from researchapp.models import Paper
       


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class UploadForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = '__all__'
