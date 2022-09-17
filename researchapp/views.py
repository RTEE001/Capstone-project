from email import message
import re
from urllib import request
from urllib.parse import uses_fragment
from wsgiref.util import request_uri
from django.shortcuts import render, redirect
from .models import Paper, Login, Role, User, Groups, University
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.text import slugify
from django.shortcuts import redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic

from .models import User
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import UserForm, GroupForm
from . import models
import operator
import itertools
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
'''
Collect items from database and pass them to a template
'''
class ALViewUser(DetailView):
    model = User
    template_name='user_detail.html'


class AEditUser(UpdateView): 
    model = User
    form_class = UserForm
    template_name = 'userEdit.html'
    success_url = reverse_lazy('listusers')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['Role'] = getRole(self.request)
        return context
  
class AEditGroup(UpdateView): 
    model = Groups
    form_class = GroupForm
    template_name = 'GroupEdit.html'
    success_url = reverse_lazy('listgroups')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['Role'] = getRole(self.request)
        return context
    
class ListUserView(generic.ListView):
    model = User
    template_name = 'list_users.html'
    context_object_name = 'users2'
    paginate_by = 4

    def get_queryset(self):
        return User.objects.order_by('-id')

def home(request):
    return render(request,'home.html')

def homelogged(request):
    return render(request,'people.html')

def researchgroup(request):
    return render(request,'researchgroup.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')


def people(request):
    return render(request,'people.html')

def research(request):
    if login1(request):
        
        return redirect('home')
    else:
        return render(request,'research.html')

def logoutView(request):
    logout(request)
    return redirect('home')
       
def signin(request):
    return render(request, 'signin.html')
    
def login1(request):
    if request.method == 'POST':
       
        try:
            m = User.objects.get(username=request.POST['username'])
            if m.check_password(request.POST['password']):
            
                request.session['username'] = request.POST['username']
                Auth_user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                if Auth_user is not None:
                    login(request, Auth_user)
                
                return redirect('dashboard')
            else:
                
                return redirect('signin')
        except User.DoesNotExist:
            return redirect('signin')
    return redirect('signin')

def index(request):
    return render(request,'index.html')

def getRole(request):
    if request.user.is_authenticated:
        
        if slugify(request.user.role)=="researcher":
            return 'Researcher'

        elif slugify(request.user.role)=="groupadmin":
            return 'GroupAdmin'

        elif slugify(request.user.role)=="uniadmin":
            return 'UniAdmin'
        
        elif slugify(request.user.role)=="cairadmin":
            return 'CAIRAdmin'

        elif slugify(request.user.role)=="student":
            return 'student'
    else:
        return 'general'


def dashboardView(request):
    return render(request,'dashboard.html', filterUsersbyrole(request))

def filterUsersbyrole(request):
    qs = User.objects.all()
    grps = Groups.objects.all()
    if getRole(request)=='GroupAdmin':
        qs = qs.filter(grp__Gname__icontains=request.user.grp)
    elif getRole(request)=="UniAdmin":
        qs = qs.filter(uni__Uniname__icontains=request.user.uni)
        grps = grps.filter(uni__Uniname__icontains=request.user.uni)
    elif getRole(request)=="Researcher":
        qs = qs.filter(grp__Gname__icontains=request.user.grp)
        qs = qs.filter(role__RoleType__icontains='student')
    
    print(grps)
    context = {
        'users': qs,
        'groups': grps,
        'Role': getRole(request),
        'UniCategory': University.objects.all()
    }
    return context


def dashboardManageUsers(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'list_users.html', filterUsersbyrole(request))


def dashboardManageGroups(request):
    return render(request, 'list_groups.html', filterUsersbyrole(request))

def createStudent(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'addStudent.html', filterUsersbyrole(request))

def createResearcher(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addResearcher.html', filterUsersbyrole(request))
    


def createGroupAdmin(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addGroupAdmin.html', filterUsersbyrole(request))


def createUniAdmin(request):
    if getRole(request)=='CAIRAdmin' :    
        return render(request, 'addUniAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')

def createCAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :  
        return render(request, 'addCAIRAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')

def create_stuUser(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    if request.method == 'POST':
            first_name=request.POST['First']
            last_name=request.POST['Last']
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['psw']
            password = make_password(password)
            if getRole(request)=='Researcher' or getRole(request)=='GroupAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), uni=University.objects.get(Uniname__exact=request.user.uni), grp=Groups.objects.get(Gname__exact=request.user.grp))
                a.save()
            elif getRole(request)=='UniAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), uni=University.objects.get(Uniname__exact=request.user.uni.Uniname), grp=Groups.objects.get(Gname__exact=request.POST['GroupCat']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), uni=University.objects.get(Uniname__exact=Groups.objects.get(Gname__exact=request.POST['GroupCat']).uni), grp=Groups.objects.get(Gname__exact=request.POST['GroupCat']))
                a.save()
    return redirect('listusers')

def create_grpAdmin(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    if request.method == 'POST':
            first_name=request.POST['First']
            last_name=request.POST['Last']
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['psw']
            password = make_password(password)
            
            if getRole(request)=='UniAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), uni=University.objects.get(Uniname__exact=request.user.uni.Uniname), grp=Groups.objects.get(Gname__exact=request.POST['GroupCat']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), uni=University.objects.get(Uniname__exact=Groups.objects.get(Gname__exact=request.POST['GroupCat']).uni), grp=Groups.objects.get(Gname__exact=request.POST['GroupCat']))
                a.save()
    return redirect('listusers')

def create_uniAdmin(request):
    if getRole(request)=='CAIRAdmin' :
        if request.method == 'POST':
                first_name=request.POST['First']
                last_name=request.POST['Last']
                username=request.POST['username']
                email=request.POST['email']
                password=request.POST['psw']
                password = make_password(password)
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='UniAdmin'), uni=University.objects.get(Uniname__exact=request.POST['UniCat']))
                a.save()
        return redirect('listusers')
    return redirect('dashboard')


def create_CAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :
        if request.method == 'POST':
                first_name=request.POST['First']
                last_name=request.POST['Last']
                username=request.POST['username']
                email=request.POST['email']
                password=request.POST['psw']
                password = make_password(password)
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='CAIRAdmin'))
                a.save()
        return redirect('listusers')
    return redirect ('dashboard')

def create_Researcher(request):
    if request.method == 'POST':
            first_name=request.POST['First']
            last_name=request.POST['Last']
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['psw']
            password = make_password(password)
            if getRole(request)=='GroupAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), uni=University.objects.get(Uniname__exact=request.user.uni), grp=Groups.objects.get(Gname__exact=request.user.grp))
                a.save()
            elif getRole(request)=='UniAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), uni=University.objects.get(Uniname__exact=request.user.uni.Uniname), grp=Groups.objects.get(Gname__exact=request.POST['GroupCat']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), uni=University.objects.get(Uniname__exact=request.POST['UniCat']), grp=Groups.objects.get(Gname__exact=request.POST['GroupCat']))
                a.save()
    return redirect('listusers')