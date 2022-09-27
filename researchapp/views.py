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
from datetime import date

'''
Python functions that takes http requests and returns http response, like HTML documents. 
A web page that uses Django is full of views with different tasks and missions
These functions hold the logic that is required to return information as a response in whatever form to the user
'''

#shared views

#dashboard view



'''
This function provides a page for the student details to be entered
The details are then passed to create_student_user to be stored in the database
'''
def createStudent(request):
    if getRole(request)=='student':
        return redirect('dashboard')
    return render(request, 'addStudent.html', filterUsersbyrole(request))

'''
This function creates a student and saves it to the database
The student is registered to the database as they are saved
'''
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

'''
This function provides a page for the researcher details to be entered
The details are then passed to create_Researcher to be stored in the database
'''
def createResearcher(request):
    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addResearcher.html', filterUsersbyrole(request))
'''
This function creates a researcher and saves it to the database
The researcher is registered to the database as they are saved
'''
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


'''
This function provides a page for the group admin details to be entered
The details are then passed to create_groupAdmin to be stored in the database
'''
def createGroupAdmin(request):

    if getRole(request)=='student' or getRole(request)=='Researcher' :
        return redirect('dashboard')
    return render(request, 'addGroupAdmin.html', filterUsersbyrole(request))

'''
This function creates a group admin and saves it to the database
The group admin is registered to the database as they are saved
'''
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
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=request.user.university.name), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                a.save()
            else:
                
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, role=Role.objects.get(RoleType__exact='GroupAdmin'), university=University.objects.get(name__exact=Group.objects.get(name__exact=request.POST['GroupCat']).university), group=Group.objects.get(name__exact=request.POST['GroupCat']))
                a.save()
    return redirect('listusers')


'''
This function provides a page for the university admin details to be entered
The details are then passed to create_uniAdmin to be stored in the database
'''
def createUniAdmin(request):
    if getRole(request)=='CAIRAdmin' :    
        return render(request, 'addUniAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')

'''
This function creates a group admin and saves it to the database
The university admin is registered to the database as they are saved
'''
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

'''
This function provides a page for the cair admin details to be entered
The details are then passed to createCAIRAdmin to be stored in the database
'''
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


'''
This function creates a group admin and saves it to the database
The cair admin is registered to the database as they are saved
'''
def createCAIRAdmin(request):
    if getRole(request)=='CAIRAdmin' :  
        return render(request, 'addCAIRAdmin.html', filterUsersbyrole(request))
    else:
        return redirect('dashboard')

'''
This function provides a page for the university details to be entered
The details are then passed to addUni to be stored in the database
'''
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
        if request.GET['type'] !='':
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