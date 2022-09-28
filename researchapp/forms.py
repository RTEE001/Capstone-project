from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pickle import TRUE
from django.forms import ModelForm
from django import forms
from researchapp.models import Contact, Group, Paper, StudentRole, University, PaperType, Role
from django.core.exceptions import ValidationError     
from datetime import date
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'


class UserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter uour username"}))
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your first name"}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your last name"}))
    
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
    university=forms.ModelChoiceField(queryset=University.objects.all(), required=False)
    student_role=forms.ModelChoiceField(queryset=StudentRole.objects.all(), required=False)
    image = forms.ImageField( required=False)
    def __init__(self,request,*args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if request.request.user.role.RoleType == "UniAdmin":
            self.fields['group'].queryset = self.fields['group'].queryset.filter(university__name__icontains= request.request.user.university.name)
            self.fields['university'].widget.attrs['disabled']=True
        elif request.request.user.role.RoleType == "CAIRAdmin":
            self.fields['group'].queryset = self.fields['group'].queryset
            self.fields['university'].widget.attrs['disabled']=True
            self.fields['student_role'].widget.attrs['disabled']=True
        else:
            self.fields['group'].widget.attrs['disabled']=True
        userupdated = User.objects.get(id=request.kwargs['pk'])
        if userupdated.role.RoleType == "CAIRAdmin" or userupdated.role.RoleType == "UniAdmin":
            self.fields['group'].widget.attrs['disabled']=True
            self.fields['student_role'].widget.attrs['disabled']=True 
        if userupdated.role.RoleType == "CAIRAdmin":
            self.fields['university'].widget.attrs['disabled']=True
        if userupdated.role.RoleType == "Researcher" or userupdated.role.RoleType == "GroupAdmin":
              self.fields['student_role'].widget.attrs['disabled']=True 
    class Meta:
        model = User
        fields = ( 'username','first_name','last_name', 'email','university', 'group', 'image')



class UploadForm(forms.ModelForm):
    published_by=forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    peerReview = forms.FileField(required=False)
    class Meta:
        model = Paper
        fields = ('title', 'author','co_author','description','category','group','publication','peerReview','published_by')
    
    def __init__(self,request,*args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.fields['published_by'].widget.attrs['disabled']=True
        self.user = request
        
     
        
    def clean(self):
        data = self.cleaned_data

        cat = data.get('category')
        if User.objects.all().filter(username=str(data.get('published_by'))).count()==0:
            self.cleaned_data['published_by']=User.objects.get(id=self.user.id)
        
        if str(cat) in ['thesis', 'dissertation', 'journal'] and data.get('peerReview') is None:
            raise ValidationError( 'peer review is a required field'
                )
        else:
            return data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('__all__')


class CreateGroupForm(forms.ModelForm):
    class meta:
        model = Group
        fields = '__all__'

class CreateUniForm(forms.ModelForm):
    class meta:
        model = University
        fields = '__all__'

class CreatePaperTypeForm(forms.ModelForm):
    class meta:
        model = PaperType
        fields = '__all__'

class CreateRoleForm(forms.ModelForm):
    class meta:
        model = Role
        fields = '__all__'