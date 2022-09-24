from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from researchapp.models import Groups, University

from django.forms import ModelForm

from django import forms
       
class GroupForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = '__all__'

class UserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter uour username"}))
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your first name"}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your last name"}))

    #username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your last name"}))


    grp = forms.ModelChoiceField(queryset=Groups.objects.all())
    class Meta:
        model = User
        fields = ( 'first_name','last_name', 'email', 'grp')

    



    



    