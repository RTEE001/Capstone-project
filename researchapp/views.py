from unicodedata import category
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import  DetailView, UpdateView
from .forms import UserForm
from django.contrib.auth import authenticate, logout
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import re
from django.db.models import Q
from itertools import chain
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


def filter_papers(request):
    papers = Paper.objects.all()
    groups = Groups.objects.all()
    unis = University.objects.all()
    type = ResearchCategory.objects.all()
    context = {
        'papers': papers,
        'groups': groups,
        'type': type,
        'unis': unis
    }
    if request.method == 'POST':
           
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        type = request.POST.get('type')
        group = request.POST.get('GroupCat')
        if startdate == '' and enddate == '' and type == '':
            print('path 1')
            return render(request, 'paper.html', context)
        elif (startdate == '' or enddate == '') and type != '':
            print('path 2')
            filter = Paper.objects.filter(category__name__contains = type)
            context ={
                'papers':filter
            }
            print(filter)
            return render(request, 'paper.html', context)

        elif startdate != '' and enddate != '' and type == '':
            print('path 3')
            filter = Paper.objects.filter(created__range = [startdate, enddate])
            print(filter)
            context ={
                'papers':filter
            }
            return render(request, 'paper.html', context)
                    
        else: 
            print('path 4')
            filter = Paper.objects.filter(created__range = [startdate, enddate], category__name__contains = type)
            print(filter)
            context = {     
                'papers':filter
        
            }
            return render(request, 'paper.html',context)
      
        
    else:
       
        return render(request, 'paper.html', context)

#

##needs work
def generate_pdf(request):
    buffer = io.BytesIO()

    pdf_object = canvas.Canvas(buffer, pagesize = letter, bottomup = 0)
    text_object =  pdf_object.beginText()
    text_object.setTextOrigin(inch, inch)
    text_object.setFont('Helvetica', 14)

    papers = Paper.objects.all()
    num_papers = papers.count()

    users = User.objects.all()
    num_users = users.count()

    unis = University.objects.all()
    num_unis = unis.count()

    uni_counts = {}

    for user in users:
        if user.uni not in uni_counts:
            uni_counts[user.uni] = {
            'uni': user.uni.__str__(),
            'count': 0
            }

        uni_counts[user.uni]['count'] += 1
        

    groups = Groups.objects.all()
    num_groups = groups.count()
    
    group_counts = {}

    for user in users:
        if user.grp not in group_counts:
            group_counts[user.grp] = {
            'group': user.grp.__str__(),
            'count': 0
            }

        group_counts[user.grp]['count'] += 1

    lines = []
    lines.append(f'Total number of papers: {num_papers}')
    lines.append(f'Total number of users: {num_users}')
    lines.append(f'Total number of groups: {num_groups}')
    for i in group_counts:
        lines.append(str(group_counts[i]))

    for i in uni_counts:
        lines.append(str(uni_counts[i]))

    lines.append(f'Total number of universities: {num_unis}')
    for line in lines:
        text_object.textLine(line)
        text_object.textLine(print())
    pdf_object.drawText(text_object)
    pdf_object.showPage()
    pdf_object.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename = 'papers_report.pdf')

def reports(request):
    return render(request, 'reports.html')

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
        return render(request,'paper.html',{'papers':paper_list} )
    else:
        display_paper = Paper.objects.all()
        return render(request, 'paper.html', {'papers':display_paper})

# def paper_filters(request):
