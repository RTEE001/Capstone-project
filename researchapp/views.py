from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic
from django.views.generic import  DetailView, UpdateView
from .forms import UserForm
from django.http import HttpResponse
import re
from django.db.models import Q


from .forms import UploadForm

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
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
       
def upload_paper(request):
 
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request, 'publication uploaded successfully')
            return render(request,'home.html')
        else:  
            messages.info(request, 'peer review is missing')
    form = UploadForm()
    return render(request, 'upload.html', {'form': form})





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


def reports(request):

    group = Groups.objects.all()
    unis = University.objects.all()
    context = {
           
            'groups': group,
            'university': unis
        }

    if request.method == 'POST':
            
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            univ= request.POST.get('uni')
            group = request.POST.get('group')

            if startdate == '' and enddate == ''  and univ =='' and group != '':
                total_papers = Paper.objects.filter(group__Gname__contains = group)
                context = {
                    'filter':total_papers 
                }
                return render(request, 'reports.html', context)

            # elif (startdate == '' or enddate == '')  and group !='' and uni !='':
            #     filter = Paper.objects.filter(category__name__contains = type)
            #     context ={
            #         'filter':filter.count()
            #     }
             
            #     return render(request, 'reports.html', context)

            # elif startdate != '' and enddate != '' and type == '':
            #     filter = Paper.objects.filter(created__range = [startdate, enddate])
              
            #     context ={
            #         'filter':filter.count()
            #     }
            #     return render(request, 'reports.html', context)
                        
            # else: 
            #     filter = Paper.objects.filter(created__range = [startdate, enddate], category__name__contains = type)
              
            #     context = {     
            #         'filter':filter.count()
            
            #     }
            #     return render(request, 'reports.html', context)       
            
    else:
    
        return render(request, 'reports.html', context)
##needs work
def generate_pdf(request):
 
    template_path = 'reports.html'
    filter = Paper.objects.filter(group__Gname__contains = request.POST['group'])
    context = {"filter":filter.count()}
    print('context begins')
   
    print(context)
    print('context ends')
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
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
        return render(request,'paper.html',{'papers':paper_list} )
    else:
        display_paper = Paper.objects.all()
        return render(request, 'paper.html', {'papers':display_paper})


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
