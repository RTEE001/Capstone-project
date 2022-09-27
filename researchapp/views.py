from django.shortcuts import render, redirect
from .models import Contact, Paper, Role, User, Group, University, StudentRole, PaperType
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic
from django.views.generic import  DetailView, UpdateView, CreateView, DeleteView, ListView
from .forms import ContactForm, UserForm
from django.http import HttpResponse
import re
from django.db.models import Q
from django.utils import timezone
from .forms import UploadForm, UserForm, GroupForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
# Create your views here.

from datetime import date

#Dashboard
'''
This fuction changes the status of the user account active to inactive
'''
def deactivate_account(request):
    user_id=request.GET['key']
    user = User.objects.get(id=user_id)
    user.is_active=False
    user.save()

    return redirect('listusers')

#Dashboard
'''
This fuction changes the status of the user account from inactive to active 
'''
def activate_account(request):
    user_id=request.GET['keys']
    user = User.objects.get(id=user_id)
    user.is_active=True
    user.save()
    return redirect('listusers')

#Dashboard
'''
This function renders all publication that are editable by a user 
depending on the type of user and allows filtering according 
to search, date, types of publicatins and groups
'''
def managePublications(request):
    searches = ''
    dates= ''
    types = ''
    group = ''

    if 'search' in request.GET:
        searches = request.GET['search']
    if 'date' in request.GET:
        dates = request.GET['date']
    if 'type' in request.GET:
        types = request.GET['type']
    if 'group' in request.GET:
        group = request.GET['group']
        
    if getRole(request)=="CAIRAdmin":
        displayPapers=filter_by_date_type_group(request, search_paper(request))
        groups = Group.objects.all()
    elif  getRole(request)=="UniAdmin":
        displayPapers=filter_by_date_type_group(request, search_paper(request)).filter(group__university__name__iexact=request.user.university)
        groups = Group.objects.all().filter(university__name__iexact=request.user.university)
    elif getRole(request)=="GroupAdmin":
        displayPapers=filter_by_date_type_group(request, search_paper(request)).filter(group__name__iexact=request.user.university)
        groups = Group.objects.all().filter(name__iexact=request.user.group)
    else :
        entry_query = get_query(str(request.user.first_name)+' '+str(request.user.last_name), ['author', 'co_author'])

        displayPapers=filter_by_date_type_group(request, search_paper(request)).filter(entry_query)
        groups = Group.objects.all().filter(name__iexact=request.user.group)
    

    context = {
        'papers': displayPapers,
        'groups': groups,
        'Role' : getRole(request),
        'type': PaperType.objects.all(), 
        'selected_search': searches,
        'selected_date': dates,
        'selected_type': types,
        'selected_group': group
    }
    return render(request, 'manageownpapers.html', context )

#Dashboard
'''
This class deletes publications
'''
class PublicationsDeleteView(DeleteView):
	model = Paper
	template_name = 'confirm_delete.html'
	success_url = reverse_lazy('managepublications')
	success_message = 'Data was deleted successfully'

#Dashboard
'''
This Class allows user to user edit profile informations and accounts
with supervisor preveliges to edit other users

'''
class EditUserProfile(generic.UpdateView):
    model = User
    form_class = UserForm
  
    template_name = 'userEdit.html'
    success_url = reverse_lazy('listusers')
    def get_context_data(self, **kwargs):
        user_id = self.kwargs['pk']
        
        context = super().get_context_data(**kwargs)
        
        context['Role'] = getRole(self.request)
        context['user'] = user_id

        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
            This is necessary to only display members that belong to a given user"""
        
        kwargs = super(EditUserProfile, self).get_form_kwargs()
        kwargs['request'] = self
        
        
        return kwargs

#Dashboard
'''
This class allows the user to edit publication details
'''
class EditPaper(generic.UpdateView):
    model = Paper
    form_class = UploadForm
    template_name ='upload.html'
    success_url = reverse_lazy('managepublications')

    def get_context_data(self, **kwargs):
        """ Passes the context object to the form class.
         This is necessary to only pass different views to different types of users"""
        context = super().get_context_data(**kwargs)
        context['Role'] = getRole(self.request)
        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display papers that belong to a given user"""
        
        kwargs = super(EditPaper, self).get_form_kwargs()
        kwargs['request'] = self.request.user
        return kwargs

#Dashboard
'''This class allows users with manage group previleges to edit group information'''
class EditGroup(UpdateView): 
    model = Group
    form_class = GroupForm
    template_name = 'GroupEdit.html'
    success_url = reverse_lazy('listgroups')
    def get_context_data(self, **kwargs):
        """ Passes the context object to the form class.
         This is necessary to only pass different views to different types of users"""
        context = super().get_context_data(**kwargs)
        
        context['Role'] = getRole(self.request)
        return context

#Dashboard

'''This function allow user with supervisor previleges to modify child user passwords'''
def passwordChange(request):
    if request.method == 'POST' and 'psw' in request.POST :
        if 'key' in request.POST:
            new_password = request.POST['psw']
            user=User.objects.get(id=request.GET['key'])
            user.set_password(new_password)
            user.save()
        
    user_id=""
    if 'key' in request.GET:
        user_id = request.GET['key']
    print('this is'+request.method )
    context={
        'users': user_id
    }

    return render(request, 'changePassword.html', context)

#Shared

'''This fuction renders the home page'''
def home(request):
    return render(request,'home.html')

#shared
'''This function renders the research groups page'''
def researchgroup(request):
    context={
        'groups': Group.objects.all()
    }
    return render(request,'researchgroup.html', context)
#shared
'''This function renders the about page '''
def about(request):
    return render(request,'about.html')

#shared
'''This function renders the contact page '''
def contact(request):
    return render(request,'contact.html')

#shared
'''This function renders the people page '''
def people(request):
    context ={
            'users': User.objects.all(),

    }
    return render(request,'people.html', context)


#shared
'''This function renders the research publication page'''
def research(request):
    return render(request,'research.html')

  
#shared
'''This function allows logged-in user to logout'''
def logoutView(request):
    logout(request)
    return redirect('home')

#shared
'''This function renders the signin page'''
def signin(request):
    return render(request, 'signin.html')

#Dashboard
'''This class allows logged in users to upload publications'''
class upload_paper(CreateView):
    model = Paper
    form_class = UploadForm
    template_name ='upload.html'
    success_url = reverse_lazy('managepublications')
    def get_context_data(self, **kwargs):
        """ Passes the context object to the form class.
         This is necessary to only pass different views to different types of users"""
        context = super().get_context_data(**kwargs)
        context['Role'] = getRole(self.request)
        
        query=""
        query_string= User.objects.all().filter(id=self.request.user.id)
        
        for i in query_string:
            query+=str(i.first_name)+" "+str(i.last_name)
        entry_query=""
        if query == " ":
            entry_query = get_query("&None&", ['author', 'co_author'])
        else:
            entry_query = get_query(query, ['author', 'co_author'])
        
        papers=Paper.objects.all().filter(entry_query)
        context['papers'] = papers
    
        return context
    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""
        
        kwargs = super(upload_paper, self).get_form_kwargs()
        kwargs['request'] = self.request.user
        
       
        return kwargs


#shared
'''This is function athencates and logs users in'''


def loginView(request):
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

#dashboard
'''This function checks and returns the type of user'''
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

#dashboard
'''This function renders the dashboard page'''
def dashboardView(request):
    return render(request,'dashboard.html', filterUsersbyrole(request))

#dashboard
'''
This function filters groups, users and returns context according to user type
'''
def filterUsersbyrole(request):
    users = User.objects.all()
    groups = Group.objects.all()
    if getRole(request)=='GroupAdmin':
        users = users.filter(group__name__icontains=request.user.group)
    elif getRole(request)=="UniAdmin":
        users = users.filter(university__name__icontains=request.user.university)
        groups = groups.filter(university__name__icontains=request.user.university)
    elif getRole(request)=="Researcher":
        users = users.filter(group__name__icontains=request.user.group)
        users = users.filter(role__RoleType__icontains='student')
    
    context = {
        'users': users,
        'groups': groups,
        'Roles' : Role.objects.all(),
        'Role': getRole(request),
        'UniCategory': University.objects.all(),
        'studentRoles': StudentRole.objects.all()
    }
    return context
#dashboard
'''This function filters and returns child users according to user type'''
def getFilteredUsers(request):
    users = User.objects.all()
    groups = Group.objects.all()
    if getRole(request)=='GroupAdmin':
        users = users.filter(group__name__icontains=request.user.group)
    elif getRole(request)=="UniAdmin":
        users = users.filter(university__name__icontains=request.user.university)
        groups = groups.filter(university__name__icontains=request.user.university)
    elif getRole(request)=="Researcher":
        users = users.filter(group__name__icontains=request.user.group)
        users = users.filter(role__RoleType__icontains='student')
    return users
#dashboard
'''This function renders page to manage child users'''
def dashboardManageUsers(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'list_users.html', filterUsersbyrole(request))
#dashboard
'''This function renders page to manage groups'''
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
            # student_role=request.POST['StudentRole']
            email=request.POST['email']
            password=request.POST['psw']
            password = make_password(password)
            if getRole(request)=='Researcher' or getRole(request)=='GroupAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), university=University.objects.get(name__exact=request.user.university), group=Group.objects.get(name__exact=request.user.grp), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                a.save()
            elif getRole(request)=='UniAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'),  group=Group.objects.get(name__exact=request.POST['GroupCat']),university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                # 
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
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), group=Group.objects.get(name__exact=request.POST['GroupCat']))
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
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='UniAdmin'), university=University.objects.get(name__exact=request.POST['UniCat']))
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
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.user.university), group=Group.objects.get(name__exact=request.user.group))
                a.save()
            elif getRole(request)=='UniAdmin':
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.POST['UniCat']), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                a.save()
    return redirect('listusers')
    #dashboard
'''This function saves universtity details in the database'''
def addUnidetails(request):
    if request.method == 'POST':
        form = (request.POST, request.FILES)
        Uname=request.POST['Acronym']
        
        instance = University(name=Uname, image=request.FILES['logo'])
        instance.save()
        return redirect('dashboard')

    return redirect('addUni')
    #dashboard
'''This funtion renders university upload form'''
def addUniversity(request):
    return render(request, 'addUni.html', filterUsersbyrole(request))
#dashboard
'''This function allow search child users by name from dashboard and filter users 
    according to particular type of user logged in'''
def filter_by_nameDashboard(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']

        entry_query = get_query(query_string, ['first_name', 'last_name'])

        return getFilteredUsers(request).filter(entry_query)
       
    else:
        return getFilteredUsers(request)

#shared
'''This function allow search users by name '''
def filter_by_nameAll(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']

        entry_query = get_query(query_string, ['first_name', 'last_name', 'university__name'])

        return User.objects.all().filter(entry_query)
       
    else:
        return User.objects.all()
    

'''This function allow search groups by name '''
def filter_group_by_nameAll(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']
        
        entry_query = get_query(query_string, ['university__name', 'name'])
        groups=Group.objects.all().filter(entry_query)
        
        return groups
       
    else:
        return Group.objects.all()
'''This function allows user to filter users according to different categories'''
def filter_by_category(request, user_list):
    
    if ('UniCat' in request.GET): 
        if request.GET['UniCat']!="":
            user_list=user_list.filter(university__name__icontains=request.GET['UniCat'])
    if ('GroupCat' in request.GET):
        if request.GET['GroupCat']!="":
            user_list=user_list.filter(group__name__icontains=request.GET['GroupCat'])
    if ('RoleCat' in request.GET):
        if request.GET['RoleCat']!="":
            user_list=user_list.filter(role__RoleType__icontains=request.GET['RoleCat'])
    return user_list

#dashboard
'''This function renders page where a supervisor can manage other users  '''

def manageUserFilter(request):
    
    found_entries = None
    if getRole(request)=="UniAdmin":    
        groups = Group.objects.all().filter(university__name__icontains=request.user.university)
                
    if getRole(request)=="CAIRAdmin":
        groups = Group.objects.all()
    user_list = filter_by_category(request,filter_by_nameDashboard(request))
    context = {
                
                'Roles': Role.objects.all(),
                'users': user_list,
                'groups': groups,
                'UniCategory': University.objects.all(),
                'Role' : getRole(request),
                'selectedUni': request.GET['UniCat'],
                'selectedRole': request.GET['RoleCat'],
                'selectedGroup': request.GET['GroupCat']

                
                }
    
    return render(request, 'list_users.html',context)
#shared
'''This function renders a page where users can search for and filter users by category'''
def searchPeopleResult(request):
    university=""
    group=""
    role=""
    query=""
    if ('UniCat' in request.GET):
        university=request.GET['UniCat']
    if ('GroupCat' in request.GET):
        group=request.GET['GroupCat']
    if ('RoleCat' in request.GET):
        role=request.GET['RoleCat']
    if ('query' in request.GET):
        query = request.GET['query']
    
    
    context ={
            'users':filter_by_category(request,filter_by_nameAll(request)),
            'groups': Group.objects.all(),
            'UniCategory': University.objects.all(),
                'selectedUni':university,
                'selectedRole': role,
                'selectedGroup': group,
                'searchName': query,
                'Roles': Role.objects.all(),

    }
    return render(request, 'PeopleSearchResults.html', context)
#shared
'''This function renders a page where users can search for and filter users by university'''
def searchGroupsResult(request):
    university=""
    
    if ('UniCat' in request.GET):
        university=request.GET['UniCat']
    
    
    
    context = {
            
            'groups': filter_by_category(request,filter_group_by_nameAll(request)),
            'UniCategory': University.objects.all(),
                'selectedUni':university,
                
    }
    return render (request, 'GroupSearchResult.html', context)

#dashboard
'''This class allow users to edit profile'''
class AViewProfile(LoginRequiredMixin,DetailView):
    model=User
    template_name = 'viewProfile.html'
    
    def get_context_data(self, **kwargs):
        context = super(AViewProfile, self).get_context_data(**kwargs)
        author_id = self.kwargs['pk']
        query=""
        query_string= User.objects.all().filter(id=author_id)
        for i in query_string:
            query+=str(i.first_name)+" "+str(i.last_name)
            
        entry_query = get_query(query, ['author', 'co_author'])
        papers=Paper.objects.all().filter(entry_query)
        
       
        context['papers'] = papers
        
        return context
#dashboard
'''This class allow users to edit group profile'''
class AViewGroupProfile(LoginRequiredMixin,DetailView):
    model=Group
    template_name = 'viewGroupProfile.html'
    
    def get_context_data(self, **kwargs):
        context = super(AViewGroupProfile, self).get_context_data(**kwargs)
        author_id = self.kwargs['pk']
        query=""
        query_string= Group.objects.all().filter(id=author_id)
        for i in query_string:
            query+=str(i.name)
            
        entry_query = get_query(query, ['name'])
        groups=Group.objects.all().filter(entry_query)       
       
        context['papers'] = groups       
        return context