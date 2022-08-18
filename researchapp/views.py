from django.shortcuts import render
from .models import Paper

# Create your views here.
'''
Collect items from database and pass them to a template
'''
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def people(request):
    return render(request, 'people.html')

def research(request):
    return render(request, 'research.html')