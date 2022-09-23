from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm
from django import forms
from researchapp.models import Paper
from django.core.exceptions import ValidationError     


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

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
