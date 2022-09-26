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

class ALViewUser(DetailView):
    model = User
    template_name='user_detail.html'


class AEditUser(generic.UpdateView): 
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
        
        kwargs = super(AEditUser, self).get_form_kwargs()
        kwargs['request'] = self
        
        
        return kwargs

class EditPaper(UpdateView):
    model = Paper
    form_class = UploadForm
    template_name ='upload.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Role'] = getRole(self.request)
        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""
        
        kwargs = super(upload_paper, self).get_form_kwargs()
        kwargs['request'] = self.request.user



class AEditGroup(UpdateView): 
    model = Group
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

def passwordChange(request):
    if request.method == 'POST' and 'psw' in request.POST :
        if 'key' in request.POST:
            new_psw = request.POST['psw']
            user=User.objects.get(id=request.GET['key'])
            user.set_password(new_psw)
            user.save()
        
    a=""
    if 'key' in request.GET:
        a = request.GET['key']
    print('this is'+request.method )
    context={
        'users': a
    }

    return render(request, 'changePassword.html', context)

def home(request):
    return render(request,'home.html')

def homelogged(request):
    return render(request,'people.html')


def researchgroup(request):
    context={
        'groups': Group.objects.all()
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


class upload_paper(CreateView):
    model = Paper
    form_class = UploadForm
    template_name ='upload.html'
    success_url = reverse_lazy('home')
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['Role'] = getRole(self.request)
        author_id = self.kwargs['pk']
        query=""
        query_string= User.objects.all().filter(id=author_id)
        for i in query_string:
            query+=str(i.first_name)+" "+str(i.last_name)
            
        entry_query = get_query(query, ['author', 'co_author'])
        a=Paper.objects.all().filter(entry_query)
        context['papers'] = a
        
        return context
    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""
        
        kwargs = super(upload_paper, self).get_form_kwargs()
        kwargs['request'] = self.request.user
        
       
        return kwargs




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
    groups = Group.objects.all()
    if getRole(request)=='GroupAdmin':
        qs = qs.filter(group__name__icontains=request.user.group)
    elif getRole(request)=="UniAdmin":
        qs = qs.filter(university__name__icontains=request.user.university)
        groups = groups.filter(university__name__icontains=request.user.university)
    elif getRole(request)=="Researcher":
        qs = qs.filter(group__name__icontains=request.user.group)
        qs = qs.filter(role__RoleType__icontains='student')
    
    context = {
        'users': qs,
        'groups': groups,
        'Roles' : Role.objects.all(),
        'Role': getRole(request),
        'UniCategory': University.objects.all(),
        'studentRoles': StudentRole.objects.all()
    }
    return context

def getFilteredUsers(request):
    qs = User.objects.all()
    groups = Group.objects.all()
    if getRole(request)=='GroupAdmin':
        qs = qs.filter(group__name__icontains=request.user.group)
    elif getRole(request)=="UniAdmin":
        qs = qs.filter(university__name__icontains=request.user.university)
        groups = groups.filter(university__name__icontains=request.user.university)
    elif getRole(request)=="Researcher":
        qs = qs.filter(group__name__icontains=request.user.group)
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

def addUnidetails(request):
    if request.method == 'POST':
        form = (request.POST, request.FILES)
        Uname=request.POST['Acronym']
        
        instance = University(name=Uname, image=request.FILES['logo'])
        instance.save()
        return redirect('dashboard')

    return redirect('addUni')

def addUni(request):
    return render(request, 'addUni.html', filterUsersbyrole(request))

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

        entry_query = get_query(query_string, ['first_name', 'last_name', 'university__name'])

        return User.objects.all().filter(entry_query)
       
    else:
        return User.objects.all()
    

def filter_group_by_nameAll(request):
    query_string = ''
    if ('query' in request.GET) and request.GET['query']!="":
        query_string = request.GET['query']
        
        entry_query = get_query(query_string, ['university__name', 'name'])
        a=Group.objects.all().filter(entry_query)
        
        return a
       
    else:
        return Group.objects.all()

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

def manageUserFilter(request):
    
    found_entries = None
    if getRole(request)=="UniAdmin":    
        groups = Group.objects.all().filter(university__name__icontains=request.user.university)
                
    if getRole(request)=="CAIRAdmin":
        groups = Group.objects.all()
    user_list = filter_by_category(request,filter_by_nameDash(request))
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
            'groups': Group.objects.all(),
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
        a=Paper.objects.all().filter(entry_query)
        
       
        context['papers'] = a
        
        return context
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
        a=Group.objects.all().filter(entry_query)       
       
        context['papers'] = a       
        return context

def filter_by_date_type_group(request, paper_list):
   
    if 'date' in request.GET:
        if request.GET['date'] !='':
            paper_list = paper_list.filter(created__icontains = request.GET['date'])
    if 'type' in request.GET:
        if request.GET['type'] !='':
            paper_list = paper_list.filter(category__name__icontains = request.GET['type'])
    if 'group' in request.GET:
        if request.GET['type'] !='':
            paper_list = paper_list.filter(group__name__icontains = request.GET['group'])

    return paper_list
    
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
#


def reports(request):
   
    context = reports_context(request)
    print(context)
    return render(request, 'reports.html', context)


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
##needs work
def generate_pdf(request):
    
  
    template_path = 'reports.html'

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    
    context = reports_context(request)
    print('request start')
    print(request.GET)
    print('context strt')
    print(context)
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
# searching 
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
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

def search_paper(request):
    
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'description','author'])

        paper_list= Paper.objects.filter(entry_query)
        return paper_list
    else:
        display_paper = Paper.objects.all()
        return display_paper

def search(request):
    
    query_string = ''
    found_entries = None
    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']

        entry_query = get_query(query_string, ['title', 'description','author'])
        entry_query_2 = get_query(query_string, ['username', 'first_name', 'last_name'])
        paper_list= Paper.objects.filter(entry_query)
        people_list = User.objects.filter(entry_query_2)
        context = {
            'papers':paper_list,
            'people': people_list
            }
        return render(request,'search.html',context )
    else:
        display_paper = Paper.objects.all()
        display_people = User.objects.all()
        context = {
            'papers':display_paper,
            'people': display_people
            }
        return render(request, 'search.html', context)

class CreateContactUs(CreateView):
    form_class = ContactForm
    model = Contact
    template_name = 'contact_form.html'
    success_url = reverse_lazy('contact_form')

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.save()
        return super().form_valid(form)


class ListMessages(ListView):
    model = Contact
    template_name = 'contact_us_list.html'

    def get_query_set(self):
        return Contact.objects.filter(date_posted__lt = timezone.now()).order_by('date_posted')