from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm
from django import forms
from researchapp.models import Contact, Group, Paper
from django.core.exceptions import ValidationError     
from datetime import date

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'


class UserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter uour username"}))
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your first name"}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your last name"}))
    
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    class Meta:
        model = User
        fields = ( 'first_name','last_name', 'email', 'group')


class UploadForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        cat = data.get('category')
        if str(cat) in ['thesis', 'dissertation', 'journal'] and data.get('peerReview') is None:
            raise ValidationError( 'peer review is a required field'
                )
        else:
            return data

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('__all__')