from contextlib import nullcontext
from email import message
import re
from unicodedata import unidata_version
from urllib import request
from urllib.parse import uses_fragment
from wsgiref.util import request_uri
from django.shortcuts import render, redirect
from .models import Paper, Role, User, Groups, University
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.text import slugify
from django.shortcuts import redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q  
import re



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
    context={
        'groups': Groups.objects.all()
    }
    return render(request,'researchgroup.html', context)

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')


def people(request):
    context ={
            'users': User.objects.all(),

    }
    return render(request,'people.html', context)

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
        'Roles' : Role.objects.all(),
        'Role': getRole(request),
        'UniCategory': University.objects.all()
    }
    return context


def getFilteredUsers(request):
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
    return qs

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



def addUnidetails(request):
    if request.method == 'POST':
        form = (request.POST, request.FILES)
        Uname=request.POST['Acronym']
        
        instance = University(Uniname=Uname, image=request.FILES['logo'])
        instance.save()
        return redirect('dashboard')

    return redirect('addUni')

def addUni(request):
    return render(request, 'addUni.html', filterUsersbyrole(request))

def normalize_query(query_string,findterms=re.compile(r'"([^"]+)"|(\S+)').findall,normspace=re.compile(r'\s{2,}').sub):

    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def filter_by_nameDash(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']

        entry_query = get_query(query_string, ['first_name', 'last_name'])

        return getFilteredUsers(request).filter(entry_query)
       
    else:
        return getFilteredUsers(request)

def filter_by_nameAll(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']

        entry_query = get_query(query_string, ['first_name', 'last_name', 'uni__Uniname'])

        return User.objects.all().filter(entry_query)
       
    else:
        return User.objects.all()
    

def filter_group_by_nameAll(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']
        
        entry_query = get_query(query_string, ['uni__Uniname', 'Gname'])
        a=Groups.objects.all().filter(entry_query)
        
        return a
       
    else:
        return Groups.objects.all()


def filter_by_category(request, user_list):
    
    if ('UniCat' in request.GET): 
        if request.GET['UniCat']!="":
            user_list=user_list.filter(uni__Uniname__icontains=request.GET['UniCat'])
    if ('GroupCat' in request.GET):
        if request.GET['GroupCat']!="":
            user_list=user_list.filter(grp__Gname__icontains=request.GET['GroupCat'])
    if ('RoleCat' in request.GET):
        if request.GET['RoleCat']!="":
            user_list=user_list.filter(role__RoleType__icontains=request.GET['RoleCat'])
    return user_list



def manageUserFilter(request):
    
    found_entries = None
    if getRole(request)=="UniAdmin":
        
        grps = Groups.objects.all().filter(uni__Uniname__icontains=request.user.uni)
                
    if getRole(request)=="CAIRAdmin":
        grps = Groups.objects.all()

    


    user_list = filter_by_category(request,filter_by_nameDash(request))
    
    

    context = {
                
                'Roles': Role.objects.all(),
                'users': user_list,
                'groups': grps,
                'UniCategory': University.objects.all(),
                'Role' : getRole(request),
                'selectedUni': request.GET['UniCat'],
                'selectedRole': request.GET['RoleCat'],
                'selectedGroup': request.GET['GroupCat']

                
                }
    
    return render(request, 'list_users.html',context)


def searchPeopleResult(request):
    a=""
    b=""
    c=""
    d=""
    if ('UniCat' in request.GET):
        a=request.GET['UniCat']
    if ('GroupCat' in request.GET):
        b=request.GET['GroupCat']
    if ('RoleCat' in request.GET):
        c=request.GET['RoleCat']
    if ('query' in request.GET):
        d = request.GET['query']
    
    
    context ={
            'users':filter_by_category(request,filter_by_nameAll(request)),
            'groups': Groups.objects.all(),
            'UniCategory': University.objects.all(),
                'selectedUni':a,
                'selectedRole': c,
                'selectedGroup': b,
                'searchName': d,
                'Roles': Role.objects.all(),

    }
    return render(request, 'PeopleSearchResults.html', context)

def searchGroupsResult(request):
    a=""
    
    if ('UniCat' in request.GET):
        a=request.GET['UniCat']
    
    
    
    context = {
            
            'groups': filter_by_category(request,filter_group_by_nameAll(request)),
            'UniCategory': University.objects.all(),
                'selectedUni':a,
                
    }

    return render (request, 'GroupSearchResult.html', context)

# def manageUserFilter(request):
   
#     query = request.GET['query']
    


#     #data = query.split()
#     data = query
#     print(len(data))
#     if( len(data) == 0):
#         return redirect('listusers')
#     else:
#                 qs=nullcontext
#                 name= data.split(" ")
#                 i=0
#                 j=1
#                 if name[0] =="Mr":
#                     return qs
#                 if len(name)==1:
                    
#                 # Searching for It
#                     qs5 =getFilteredUsers(request).filter(first_name__iexact=name[i]).distinct()
#                     qs6 =getFilteredUsers(request).filter(first_name__exact=name[i]).distinct()

#                     qs7 =getFilteredUsers(request).filter(first_name__contains=name[i])
#                     qs8 =getFilteredUsers(request).select_related().filter(first_name__contains=name[i]).distinct()
#                     qs9 =getFilteredUsers(request).filter(first_name__startswith=name[i]).distinct()
#                     qs10 =getFilteredUsers(request).filter(first_name__endswith=name[i]).distinct()
#                     qs11 =getFilteredUsers(request).filter(first_name__istartswith=name[i]).distinct()
#                     qs12 =getFilteredUsers(request).filter(first_name__icontains=name[i])
#                     qs13 =getFilteredUsers(request).filter(first_name__iendswith=name[i]).distinct()

#                     qs14 =getFilteredUsers(request).filter(last_name__iexact=name[i]).distinct()
#                     qs15 =getFilteredUsers(request).filter(last_name__exact=name[i]).distinct()

#                     qs16 =getFilteredUsers(request).all().filter(last_name__contains=name[i])
#                     qs17 =getFilteredUsers(request).select_related().filter(last_name__contains=name[i]).distinct()
#                     qs18 =getFilteredUsers(request).filter(last_name__startswith=name[i]).distinct()
#                     qs19 =getFilteredUsers(request).filter(last_name__endswith=name[i]).distinct()
#                     qs20 =getFilteredUsers(request).filter(last_name__istartswith=name[i]).distinct()
#                     qs21 =getFilteredUsers(request).filter(last_name__icontains=name[i])
#                     qs22 =getFilteredUsers(request).filter(last_name__iendswith=name[i]).distinct()

#                     files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13, qs14, qs15, qs16, qs17, qs18, qs19, qs20, qs21, qs22)
#                 else:
                    
#                     qs5 =getFilteredUsers(request).filter(first_name__iexact=name[i],last_name__iexact=name[j]).distinct()
#                     qs6 =getFilteredUsers(request).filter(first_name__exact=name[i],last_name__iexact=name[j]).distinct()

#                     files = itertools.chain(qs5, qs6)

#                 res = []
#                 for i in files:
#                     if i not in res:
#                         res.append(i)
#                 if getRole(request)=="UniAdmin":
        
#                     grps = Groups.objects.all().filter(uni__Uniname__icontains=request.user.uni)
                
#                 if getRole(request)=="CAIRAdmin":
#                     grps = Groups.objects.all()
#                 grps = nullcontext
#                 print(files)
#                 # word variable will be shown in html when user click on search button
#                 context = {
#                 
#                 'Role': getRole(request),
#                 'groups': grps,
#                 'UniCategory': University.objects.all()
#                 }
                
#                 return render(request, 'list_users.html',context)



