'''
Python functions that takes http requests and returns http response, like HTML documents. 
A web page that uses Django is full of views with different tasks and missions
These functions hold the logic that is required to return information as a response in whatever form to the user
'''

import smtplib
from email.mime.text import MIMEText
from django.shortcuts import render, redirect
from .models import Contact, Paper, Role, User, Group, University, StudentRole, PaperType
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic
from django.views.generic import  DetailView, UpdateView, CreateView, DeleteView, ListView
from .forms import ContactForm, CreatePaperTypeForm, UserForm, CreateGroupForm, CreateUniForm, CreatePaperTypeForm, CreateRoleForm
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
from datetime import date
import os
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
#Dashboard

'''
This function sends an email to a user whenever a user's account is deactivated
'''
def email_notif_deactivate(email_address):
    load_dotenv()
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SENDER_EMAIL_ADDRESS = os.getenv("SMTP_LOGIN")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") 

    body = f"Your account with CAIR has been deactivated."
    msg = MIMEText(body)
    msg["Subject"] = 'Account activation'
    msg["From"] = SENDER_EMAIL_ADDRESS
    msg["To"] = email_address

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(SENDER_EMAIL_ADDRESS, SMTP_PASSWORD)
    smtp.sendmail(SENDER_EMAIL_ADDRESS,email_address, msg.as_string())
    smtp.quit()

'''
This fuction changes the status of the user account active to inactive
'''
def deactivate_account(request):
    user_id=request.GET['key']
    user = User.objects.get(id=user_id)
    user.is_active=False
    user.save()
    email = user.email
    email_notif_deactivate(email)
    return redirect('listusers')

#Dashboard


'''
This function sends an email to a user whenever a user's account is activated
'''
def email_notif_activate(email_address):
    load_dotenv()
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SENDER_EMAIL_ADDRESS = os.getenv("SMTP_LOGIN")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") 

    body = f"Your account with CAIR has been activated."
    msg = MIMEText(body)
    msg["Subject"] = 'Account activation'
    msg["From"] = SENDER_EMAIL_ADDRESS
    msg["To"] = email_address

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(SENDER_EMAIL_ADDRESS, SMTP_PASSWORD)
    smtp.sendmail(SENDER_EMAIL_ADDRESS,email_address, msg.as_string())
    smtp.quit()

'''
This fuction changes the status of the user account from inactive to active 
'''
def activate_account(request):
    user_id=request.GET['keys']
    user = User.objects.get(id=user_id)
    user.is_active=True
    user.save()
    email = user.email 
    email_notif_activate(email)
    return redirect('listusers')

#Dashboard
'''
This function renders all publication that are editable by a user 
depending on the type of user and allows filtering according 
to search, date, types of publicatins and groups
'''
@login_required
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
    elif getRole(request)=="GroupAdmin" or getRole(request)=="GroupLeader":
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

class PublicationsDeleteView(LoginRequiredMixin,DeleteView):
	model = Paper
	template_name = 'confirm_delete.html'
	success_url = reverse_lazy('managepublications')
	success_message = 'Data was deleted successfully'

#Dashboard
'''
This Class allows user to user edit profile informations and accounts
with supervisor preveliges to edit other users

'''

class EditUserProfile(LoginRequiredMixin,generic.UpdateView):
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

class EditPaper(LoginRequiredMixin,generic.UpdateView):
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

class EditGroup(LoginRequiredMixin,UpdateView): 
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
@login_required
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
@login_required
def logoutView(request):
    logout(request)
    return redirect('home')

#shared
'''This function renders the signin page'''
def signin(request):
    return render(request, 'signin.html')

#Dashboard
'''This class allows logged in users to upload publications'''

class upload_paper(LoginRequiredMixin,CreateView):
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
            user = User.objects.get(username=request.POST['username'])
            if user.check_password(request.POST['password']):
            
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

        elif slugify(request.user.role) == 'groupleader':
            return 'GroupLeader'
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
@login_required
def dashboardView(request):
    return render(request,'dashboard.html', filterUsersbyrole(request))

#dashboard
'''
This function filters groups, users and returns context according to user type
'''
def filterUsersbyrole(request):
    users = User.objects.all()
    groups = Group.objects.all()
    if getRole(request)=='GroupAdmin' or getRole(request)=="GroupLeader":
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
    if getRole(request)=='GroupAdmin' or getRole(request)=="GroupLeader":
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
@login_required
def dashboardManageUsers(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'list_users.html', filterUsersbyrole(request))
#dashboard
'''This function renders page to manage groups'''
@login_required
def dashboardManageGroups(request):
    return render(request, 'list_groups.html', filterUsersbyrole(request))
@login_required
def createStudent(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'addStudent.html', filterUsersbyrole(request))
@login_required
def createResearcher(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addResearcher.html', filterUsersbyrole(request))
    

@login_required
def createGroupAdmin(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addGroupAdmin.html', filterUsersbyrole(request))
@login_required
def createGroupLeader(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addGroupLeader.html', filterUsersbyrole(request))

@login_required
def createUniAdmin(request):
    if getRole(request)=='CAIRAdmin' :    
        return render(request, 'addUniAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')
@login_required
def createCAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :  
        return render(request, 'addCAIRAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')
@login_required
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
            if getRole(request)=='Researcher' or getRole(request)=='GroupAdmin' or getRole(request)=='GroupLeader':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), university=University.objects.get(name__exact=request.user.university), group=Group.objects.get(name__exact=request.user.grp), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                user.save()
                email_notif(email)
            elif getRole(request)=='UniAdmin':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))      
                user.save()
                email_notif(email)
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'),  group=Group.objects.get(name__exact=request.POST['GroupCat']),university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                user.save()
                email_notif(email)
                
    return redirect('listusers')
@login_required
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
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email)
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email)
    return redirect('listusers')
@login_required
def create_grpLeader(request):
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
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupLeader'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email)
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupLeader'), university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email)
    return redirect('listusers')
@login_required
def create_uniAdmin(request):
    if getRole(request)=='CAIRAdmin' :
        if request.method == 'POST':
                first_name=request.POST['First']
                last_name=request.POST['Last']
                username=request.POST['username']
                email=request.POST['email']
                password=request.POST['psw']
                password = make_password(password)
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='UniAdmin'), university=University.objects.get(name__exact=request.POST['UniCat']))
                user.save()
                email_notif(email)
        return redirect('listusers')
    return redirect('dashboard')
@login_required
def create_CAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :
        if request.method == 'POST':
                first_name=request.POST['First']
                last_name=request.POST['Last']
                username=request.POST['username']
                email=request.POST['email']
                password=request.POST['psw']
                password = make_password(password)
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='CAIRAdmin'))
                user.save()
                email_notif(email)
        return redirect('listusers')
    return redirect ('dashboard')
@login_required
def create_Researcher(request):
    if request.method == 'POST':
            first_name=request.POST['First']
            last_name=request.POST['Last']
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['psw']
            password = make_password(password)
            if getRole(request)=='GroupAdmin' or getRole(request)=='GroupLeader':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.user.university), group=Group.objects.get(name__exact=request.user.group))
                user.save()
            elif getRole(request)=='UniAdmin':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.POST['UniCat']), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email)
    return redirect('listusers')
    #dashboard

'''This function saves universtity details in the database'''
@login_required
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
@login_required
def addUniversity(request):
    return render(request, 'addUni.html', filterUsersbyrole(request))
#dashboard
'''This function allow search child users by name from dashboard and filter users 
    according to particular type of user logged in'''
@login_required
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
@login_required
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
class AViewProfile(DetailView):
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

class DViewProfile(DetailView):
    model=User
    template_name = 'dviewProfile.html'
    
    def get_context_data(self, **kwargs):
        context = super(DViewProfile, self).get_context_data(**kwargs)
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
class AViewGroupProfile(DetailView):
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
        papers=Paper.objects.filter(group__exact = Group.objects.get(name=query))      
        
        context['papers'] = papers      
        return context

#shared views

#dashboard view



'''
This function provides a page for the student details to be entered
The details are then passed to create_student_user to be stored in the database
'''
@login_required
def createStudent(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'addStudent.html', filterUsersbyrole(request))

'''
This function creates a student and saves it to the database
The student is registered to the database as they are saved
'''

def email_notif(email_address, username, password):
    load_dotenv()
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SENDER_EMAIL_ADDRESS = os.getenv("SMTP_LOGIN")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") 

    body = f"Your account with CAIR has been activated. Your username is {username} and your password is {password}"
    msg = MIMEText(body)
    msg["Subject"] = 'Account activation'
    msg["From"] = SENDER_EMAIL_ADDRESS
    msg["To"] = email_address

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(SENDER_EMAIL_ADDRESS, SMTP_PASSWORD)
    smtp.sendmail(SENDER_EMAIL_ADDRESS,email_address, msg.as_string())
    smtp.quit()

@login_required
def create_studentUser(request):
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
            if getRole(request)=='Researcher' or getRole(request)=='GroupAdmin' or getRole(request)=='GroupLeader':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), university=University.objects.get(name__exact=request.user.university), group=Group.objects.get(name__exact=request.user.grp), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
            elif getRole(request)=='UniAdmin':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='student'),  group=Group.objects.get(name__exact=request.POST['GroupCat']),university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), student_role=StudentRole.objects.get(name__exact=request.POST['studentRole']))      
                user.save()
                email_notif(email, username, request.POST['psw'] )
                
                
    return redirect('listusers')

'''
This function provides a page for the researcher details to be entered
The details are then passed to create_Researcher to be stored in the database
'''
@login_required
def createResearcher(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addResearcher.html', filterUsersbyrole(request))
'''
This function creates a researcher and saves it to the database
The researcher is registered to the database as they are saved
'''
@login_required
def create_Researcher(request):
    if request.method == 'POST':
            first_name=request.POST['First']
            last_name=request.POST['Last']
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['psw']
            password = make_password(password)
            if getRole(request)=='GroupAdmin' or getRole(request)=='GroupLeader':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.user.university), group=Group.objects.get(name__exact=request.user.group))
                user.save()
                email_notif(email, username, request.POST['psw'] )
            elif getRole(request)=='UniAdmin':
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='Researcher'), university=University.objects.get(name__exact=request.POST['UniCat']), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
    return redirect('listusers')


'''
This function provides a page for the group admin details to be entered
The details are then passed to create_groupAdmin to be stored in the database
'''
@login_required
def createGroupAdmin(request):

    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addGroupAdmin.html', filterUsersbyrole(request))


'''
This function creates a group admin and saves it to the database
The group admin is registered to the database as they are saved
'''
@login_required
def create_groupAdmin(request):
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
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
    return redirect('listusers')

@login_required
def create_groupLeader(request):
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
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupLeader'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
            else:
                
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupLeader'), university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
    return redirect('listusers')


'''
This function provides a page for the university admin details to be entered
The details are then passed to create_uniAdmin to be stored in the database
'''
@login_required
def createUniAdmin(request):
    if getRole(request)=='CAIRAdmin' :    
        return render(request, 'addUniAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')

'''
This function creates a group admin and saves it to the database
The university admin is registered to the database as they are saved
'''
@login_required
def create_uniAdmin(request):
    if getRole(request)=='CAIRAdmin' :
        if request.method == 'POST':
                first_name=request.POST['First']
                last_name=request.POST['Last']
                username=request.POST['username']
                email=request.POST['email']
                password=request.POST['psw']
                password = make_password(password)
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='UniAdmin'), university=University.objects.get(name__exact=request.POST['UniCat']))
                user.save()
                email_notif(email, username, request.POST['psw'] )
        return redirect('listusers')
    return redirect('dashboard')

'''
This function provides a page for the cair admin details to be entered
The details are then passed to createCAIRAdmin to be stored in the database
'''
@login_required
def create_CAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :
        if request.method == 'POST':
                first_name=request.POST['First']
                last_name=request.POST['Last']
                username=request.POST['username']
                email=request.POST['email']
                password=request.POST['psw']
                password = make_password(password)
                user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='CAIRAdmin'))
                user.save()
                email_notif(email, username, request.POST['psw'] )
        return redirect('listusers')
    return redirect ('dashboard')


'''
This function creates a group admin and saves it to the database
The cair admin is registered to the database as they are saved
'''
@login_required
def createCAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :  
        return render(request, 'addCAIRAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')

'''
This function provides a page for the university details to be entered
The details are then passed to addUni to be stored in the database
'''
@login_required
def addUnidetails(request):
    if request.method == 'POST':
        form = (request.POST, request.FILES)
        Uname=request.POST['Acronym']
        
        instance = University(name=Uname, image=request.FILES['logo'])
        instance.save()
        return redirect('dashboard')

    return redirect('addUni')

'''
This function creates a university and saves it to the database
The unoversity is registered to the database as they are saved
'''
@login_required
def addUni(request):
    return render(request, 'addUni.html', filterUsersbyrole(request))

#admin view
'''
This function returns the context of the reports page after the user enters filters
If no filters are entered the default filters are used and the context is returned
If a group is selected, only context relating to that group is returned
If a university is selected, only context relating to that univeristy is returned
If no group or univeristy is chosen, the context of the whole database is returned 
'''
def reports_context(request):
    startdate_present = False
    enddate_present = False
    group_present = False
    university_present = False

    startdate = '2000-01-01'
    enddate = str(date.today())  
    group = ''
    university = ''
    context = {
        
        'startdate': startdate,
        'enddate': enddate,
        'unis': University.objects.all(),
        'groups': Group.objects.all(),
        'type': PaperType.objects.all(),
   
    }
    
    if 'startdate' in request.GET:
        if request.GET['startdate'] != '':
            startdate_present = True
            startdate = request.GET['startdate']      
    if 'enddate' in request.GET:
        if request.GET['enddate'] != '':
            enddate_present = True
            enddate = request.GET['enddate']
      
    if 'group' in request.GET:
       
        if request.GET['group'] != '':
            group_present = True
            group = request.GET['group']          
    
    if 'university' in request.GET:
        if request.GET['university'] != '':
            university_present = True
            university = request.GET['university']

    if group_present == False and university_present == False:
        if startdate_present == True and enddate_present ==False:
            context['startdate'] = startdate
        elif startdate_present == True and enddate_present == True:
            context['startdate'] = startdate
            context['enddate'] = enddate
        elif startdate_present ==False and enddate_present ==True:
            context['enddate'] = enddate

        context['total_number_of_users'] = User.objects.filter(date_joined__range = [startdate, enddate]).count()
        context['total_number_of_universities'] = University.objects.filter(created__range = [startdate, enddate]).count()
        context['total_number_of_groups'] = Group.objects.filter(created__range = [startdate, enddate]).count()
        context['total_number_of_publications'] = Paper.objects.filter(created__range = [startdate, enddate]).count()

        each_university_users_dict = {}
        each_university_publications_dict = {}
        each_university_masters_dict = {}
        each_university_phd_dict = {}
        each_university_researchers_dict = {}
        each_university_graduates_dict = {}
      

        all_unis = University.objects.filter(created__range = [startdate, enddate])

        for each_uni in all_unis:
            
            each_university_users_dict[each_uni.name] = User.objects.filter(group__university__name__contains = each_uni, date_joined__range = [startdate, enddate]).count()
            each_university_publications_dict[each_uni.name]= Paper.objects.filter(group__university__name__contains = each_uni, created__range = [startdate, enddate]).count()
            each_university_masters_dict[each_uni.name]= User.objects.filter(group__university__name__contains = each_uni, date_joined__range = [startdate, enddate], student_role__name__contains = 'masters').count()
            each_university_phd_dict[each_uni.name]= User.objects.filter(group__university__name__contains = each_uni, date_joined__range = [startdate, enddate], student_role__name__contains = 'phd').count()
            each_university_researchers_dict[each_uni.name]= User.objects.filter(group__university__name__contains = each_uni, date_joined__range = [startdate, enddate], student_role__name__contains = 'Researcher').count()   
            each_university_graduates_dict[each_uni.name]= User.objects.filter(group__university__name__contains = each_uni, date_joined__range = [startdate, enddate], student_role__name__contains = 'graduate').count()            

        context['each_university_users_dict'] = (str(each_university_users_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_university_publications_dict'] = (str(each_university_publications_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_university_masters_dict'] = (str(each_university_masters_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_university_phd_dict'] = (str(each_university_phd_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_university_researchers_dict'] = (str(each_university_researchers_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_university_graduates_dict'] = (str(each_university_graduates_dict).replace("{","").replace("}", "")).replace(',', '\n')  

    elif group_present == True and university_present == False:
  
        if startdate_present == True and enddate_present ==False:
            context['startdate'] = startdate
        elif startdate_present == True and enddate_present == True:
            context['startdate'] = startdate
            context['enddate'] = enddate
        elif startdate_present ==False and enddate_present ==True:
            context['enddate'] = enddate
        context['total_number_of_users_in_group'] = User.objects.filter(date_joined__range = [startdate, enddate],  group__name__contains = group).count()

        group_publications_dict = {}
        group_masters_dict = {}
        group_phd_dict = {}
        group_researchers_dict = {}
        group_graduates_dict = {}

        group_publications_dict[group] =  Paper.objects.filter(group__name__contains = group, created__range = [startdate, enddate]).count()
        group_masters_dict[group] = User.objects.filter(group__name__contains = group, date_joined__range = [startdate, enddate], student_role__name__contains = 'masters').count()
        group_phd_dict[group] = User.objects.filter(group__name__contains = group, date_joined__range = [startdate, enddate], student_role__name__contains = 'phd').count()
        group_researchers_dict[group] = User.objects.filter(group__name__contains = group, date_joined__range = [startdate, enddate], student_role__name__contains = 'Researcher').count()
        group_graduates_dict[group] = User.objects.filter(group__name__contains = group, date_joined__range = [startdate, enddate], student_role__name__contains = 'graduate').count()

        context['group_publications_dict'] = (str(group_publications_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['group_masters_dict'] = (str(group_masters_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['group_phd_dict'] = (str(group_phd_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['group_researchers_dict'] = (str(group_researchers_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['group_graduates_dict'] = (str(group_graduates_dict).replace("{","").replace("}", "")).replace(',', '\n')

    elif  group_present == False and university_present == True:
        if startdate_present == True and enddate_present ==False:
            context['startdate'] = startdate
        elif startdate_present == True and enddate_present == True:
            context['startdate'] = startdate
            context['enddate'] = enddate
        elif startdate_present ==False and enddate_present ==True:
            context['enddate'] = enddate
        context['total_number_of_users_in_uni'] = User.objects.filter(date_joined__range = [startdate, enddate], university__name__contains = university ).count()
       
        context['total_number_of_groups'] = Group.objects.filter(created__range = [startdate, enddate], university__name__contains = university).count()
        context['total_number_of_publications'] = Paper.objects.filter(created__range = [startdate, enddate], group__university__name__contains = university).count()


        each_group_users_dict = {}
        each_group_publications_dict = {}
        each_group_masters_dict = {}
        each_group_phd_dict = {}
        each_group_researchers_dict = {}
        each_group_graduates_dict = {}
      

        all_groups_in_uni = Group.objects.filter(created__range = [startdate, enddate], university__name__contains = university )

        for each_group in all_groups_in_uni:
            
            each_group_users_dict[each_group.name] = User.objects.filter(group__name__contains = each_group, date_joined__range = [startdate, enddate]).count()
            each_group_publications_dict[each_group.name]= Paper.objects.filter(group__name__contains = each_group, created__range = [startdate, enddate]).count()
            each_group_masters_dict[each_group.name]= User.objects.filter(group__name__contains = each_group, date_joined__range = [startdate, enddate], student_role__name__contains = 'masters').count()
            each_group_phd_dict[each_group.name]= User.objects.filter(group__name__contains = each_group, date_joined__range = [startdate, enddate], student_role__name__contains = 'phd').count()
            each_group_researchers_dict[each_group.name]= User.objects.filter(group__name__contains = each_group, date_joined__range = [startdate, enddate], student_role__name__contains = 'Researcher').count()   
            each_group_graduates_dict[each_group.name]= User.objects.filter(group__name__contains = each_group, date_joined__range = [startdate, enddate], student_role__name__contains = 'graduate').count()            

        context['each_group_users_dict'] = (str(each_group_users_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_group_publications_dict'] = (str(each_group_publications_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_group_masters_dict'] = (str(each_group_masters_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_group_phd_dict'] = (str(each_group_phd_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_group_researchers_dict'] = (str(each_group_researchers_dict).replace("{","").replace("}", "")).replace(',', '\n')
        context['each_group_graduates_dict'] = (str(each_group_graduates_dict).replace("{","").replace("}", "")).replace(',', '\n')
     
    context['selected_group'] = group
    context['selected_university'] = university
    return context

#admin view
'''
This function provides the view of the report to the user
'''
@login_required
def reports(request):
    context = reports_context(request)
    return render(request, 'reports.html', context)


#admin dashboard view
'''
This function generates the report for the admins.
It passes the context returned after a filter is applied
or uses the default filters if no filters are applied by the user
'''
def generate_pdf(request):
    
    template_path = 'reports.html'
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'   
    context = reports_context(request)
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show  erroe
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# searching 
''' 
Splits the query string in invidual keywords, getting rid of unecessary spaces
and grouping quoted words together.
'''
def normalize_query(query_string,findterms=re.compile(r'"([^"]+)"|(\S+)').findall,normspace=re.compile(r'\s{2,}').sub):  
    return [normspace(' ', (term[0] or term[1]).strip()) for term in findterms(query_string)]

''' 
Returns a query, that is a combination of Q objects. That combination
aims to search keywords within a model by testing the given search fields.
'''
def get_query(query_string, search_fields):
    
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            queries = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = queries
            else:
                or_query = or_query | queries
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

#shared view
'''
This function searches through the entire database for matches of the user input
The function looks through for matches in all the publivations 
and returns it to the user view
'''

##needs work
def search_paper(request):
    
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'description','author'])
        
        paper_list= Paper.objects.filter(entry_query)
        return paper_list
    elif ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']

        entry_query = get_query(query_string, ['title', 'description','author'])

        paper_list= Paper.objects.filter(entry_query)
        return paper_list
    else:
        display_paper = Paper.objects.all()
        return display_paper


#shared view

'''
This function searches through the entire database for matches of the user input
The function looks through for matches in all the publivations, users and groups 
and returns it to the user view
'''
def search(request):
    
    query_string = ''
    found_entries = None
    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']

        entry_query = get_query(query_string, ['title', 'description','author'])
        entry_query_2 = get_query(query_string, ['username', 'first_name', 'last_name'])
        entry_query_3 = get_query(query_string, ['name'])
        paper_list= Paper.objects.all().filter(entry_query)
        people_list = User.objects.all().filter(entry_query_2)
        group_list = Group.objects.all().filter(entry_query_3)
        context = {
            'papers':paper_list,
            'people': people_list,
            'groups' : group_list
            }
        return render(request,'search.html',context )
    else:
        display_paper = Paper.objects.all()
        display_people = User.objects.all()
        group_list = Group.objects.all()
        context = {
            'papers':display_paper,
            'people': display_people,
            'groups' : group_list
            }
        return render(request, 'search.html', context)

#filter helper
'''
This function is a helper function to the filter papers function
It filters by date, then by typ, then by group and returns the filtered set
'''
def filter_by_date_type_group(request, paper_list):
       
    if 'date' in request.GET:
        if request.GET['date'] !='':
            paper_list = paper_list.filter(created__icontains = request.GET['date'])
    if 'type' in request.GET:
        if request.GET['type'] !='':
            paper_list = paper_list.filter(category__name__icontains = request.GET['type'])
    if 'group' in request.GET:
        if request.GET['group'] !='':
            paper_list = paper_list.filter(group__name__icontains = request.GET['group'])

    return paper_list

#shared view
'''
This function filters the papers/publications 
It allows for filtering by searching via text, 
filtering by year published, 
filtering by types and filtering by group
'''  
def filter_papers(request):
    
    searches = ''
    dates= ''
    types = ''
    groups = ''

    if 'search' in request.GET:
        searches = request.GET['search']
    if 'date' in request.GET:
        dates = request.GET['date']
    if 'type' in request.GET:
        types = request.GET['type']
    if 'group' in request.GET:
        groups = request.GET['group']

    context = {
        'papers': filter_by_date_type_group(request, search_paper(request)),
        'groups': Group.objects.all(),
        'type': PaperType.objects.all(), 
        'selected_search': searches,
        'selected_date': dates,
        'selected_type': types,
        'selected_group': groups
    }  
    return render(request, 'paper.html', context)
#shared view
'''
This class creates the view where the form for contacting the admin is rendered to the user
The user may want to request a new password or contact the admin on any other matter
'''
class CreateContactUs(CreateView):
    form_class = ContactForm
    model = Contact
    template_name = 'contact_form.html'
    success_url = reverse_lazy('home')

    
    def form_valid(self, form):
        '''This method checks that the information passed into the form is valid'''
        self.object = form.save(commit = False)
        self.object.save()
        return super().form_valid(form)


#dashboard
'''
This class lists the messages that the administrator has on the dashboard
Messages are either from users who require a change of password or 
users who want to contact the admin
'''
class ListMessages(ListView):
    model = Contact
    template_name = 'message_list.html'
  
    def get_queryset(self):
        '''This method returns the query set of the messages that are currently in the database
        The messages are ordered by date from the latest one to the oldest one'''
        return Contact.objects.filter(date_posted__lt = timezone.now()).order_by('-date_posted')


'''
This class renders the contact us page used by users to send messages to the admin
'''
class Contacts(CreateView):
    form_class = ContactForm
    model = Contact
    template_name = 'contact.html'
    success_url = reverse_lazy('home')

    
    def form_valid(self, form):
        '''This method checks that the information passed into the form is valid'''
        self.object = form.save(commit = False)
        self.object.save()
        return super().form_valid(form)
