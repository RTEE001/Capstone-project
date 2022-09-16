from email import message
from urllib.parse import uses_fragment
from django.shortcuts import render, redirect
from .models import Paper, Login, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.shortcuts import redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic

from .models import User
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import UserForm
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


class AEditUser(SuccessMessageMixin, UpdateView): 
    model = User
    form_class = UserForm
    template_name = 'userEdit.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully updated"
    
class ListUserView(generic.ListView):
    model = User
    template_name = 'list_users.html'
    context_object_name = 'users'
    paginate_by = 4

    def get_queryset(self):
        return User.objects.order_by('-id')

def home(request):
    login1(request)
    return render(request,'home.html')

def homelogged(request):
    if login1(request):
        
        return redirect('home')
    else:
        return render(request,'people.html')

def about(request):
    if login1(request):
        
        return redirect('home')
    else:
        return render(request,'about.html')

def contact(request):

    if login1(request):
        
        return redirect('home')
    else:
        return render(request,'contact.html')


def people(request):
    
    if login1(request):
        
        return redirect('home')
    else:
        return render(request,'people.html')

def research(request):
    if login1(request):
        
        return redirect('home')
    else:
        return render(request,'research.html')

def logoutView(request):
    logout(request)
    return redirect('home')
       

def login1(request):
    if request.method == 'POST':
       
        try:
            m = User.objects.get(username=request.POST['uname'])
            if m.check_password(request.POST['psw']):
            
                request.session['username'] = request.POST['uname']
                Auth_user = authenticate(request, username=request.POST['uname'], password=request.POST['psw'])
                if Auth_user is not None:
                    login(request, Auth_user)
                
                return True
            else:
                print("not") 
                return False
        except User.DoesNotExist:
            return False
    return False

def index(request):
    return render(request,'index.html')

def h(request):
    return render(request,'h.html')

def show_paper_results(request):
    if request.method == 'POST':
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        search_result = Paper.objects.filter(created__range = [startdate, enddate])
        return render(request, 'paper.html', {'papers': search_result})
    else:
        display_paper = Paper.objects.all()
        return render(request, 'paper.html', {'papers':display_paper})