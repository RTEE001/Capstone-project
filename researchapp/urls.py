"""
Django runs through each URL pattern, in order, and stops at the first one that matches the requested URL, 
matching against path_info . 
Once one of the URL patterns matches, Django imports and calls the given view, 
which is a Python function (or a class-based view)
"""


from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('contact/',views.Contacts.as_view(), name = 'contact'),
    path('people/',views.people, name = 'people'),
    path('research/', views.research, name = 'research'),
    path('logged/',views.loginView, name = 'loggedin'),
    path('logout/',views.logoutView, name = 'loggedout'),

    path('researchgroup/', views.researchgroup, name = 'researchgroup'),
    path('signin/', views.signin, name = 'signin'),
    path('searchPeopleResult/', views.searchPeopleResult, name = 'searchPeopleResult'),
    path('searchGroupResult/', views.searchGroupsResult,name='searchGroupResult'),
    path('avprofle/<int:pk>', views.AViewProfile.as_view(), name='avprofile'),
    path('dprofle/<int:pk>', views.DViewProfile.as_view(), name='dvprofile'),
    path('avGprofle/<int:pk>', views.AViewGroupProfile.as_view(), name='avGprofile'),

    path('contact_form/', views.CreateContactUs.as_view(), name = 'contact_form'),
    path('list_chats/', views.ListMessages.as_view(), name = 'contact_list'),
    path('papers/', views.filter_papers, name = 'papers'),
    path('reports/', views.reports, name = 'reports'),
    path('papers_pdf/', views.generate_pdf, name = 'paperpdf'),
    path('search_paper/', views.search_paper, name="search_paper"),
    path('upload/', views.upload_paper.as_view(), name = 'upload'),
    path('search/', views.search, name = 'search'),

 
#dashboard
   
    path('listusers/', views.dashboardManageUsers, name= 'listusers'),
    path('dashboard/',views.dashboardView, name = 'dashboard'),
    path('listgroups/', views.dashboardManageGroups, name ='listgroups'),   
    path('aegroup/<int:pk>', views.EditGroup.as_view(), name='aegroup'),
    path('aeuser/<int:pk>', views.EditUserProfile.as_view(), name='aeuser'),
    path('addstu/', views.createStudent, name='addstu'),
    path('addGA/', views.createGroupAdmin, name='addGA'),
    path('addGL/', views.createGroupLeader, name='addGL'),
    path('addUA/', views.createUniAdmin, name='addUA'),
    path('addCA/', views.createCAIRAdmin, name='addCA'),
    path('addR/', views.createResearcher, name='addR'),
    path('createStuUser/', views.create_studentUser, name= 'createStuUser'),
    path('createGAUser/', views.create_groupAdmin, name= 'createGAUser'),
    path('createGLUser/', views.create_groupLeader, name= 'createGLUser'),
    path('createUAUser/', views.create_uniAdmin, name= 'createUAUser'),
    path('createCAUser/', views.create_CAIRAdmin, name= 'createCAUser'),
    path('createRUser/', views.create_Researcher, name= 'createRUser'),
    path('change_password', views.passwordChange, name='change_password'),
    path('manageusersearch/',views.manageUserFilter, name ='manageusersearch'), 
    path('addUni/', views.addUniversity, name= 'addUni'),
    path('addUnidetails,', views.addUnidetails, name= 'addUnidetails'),
    path('editpaper/<int:pk>', views.EditPaper.as_view(),name='editPaper'),
    path('list_chats/', views.ListMessages.as_view(), name = 'contact_list'),
    path('managepublications/', views.managePublications, name ='managepublications'),
    path('activate/', views.activate_account, name= 'activate'),
    path('deactivate/', views.deactivate_account, name= 'deactivate'),
    path('Deletepaper/<int:pk>', views.PublicationsDeleteView.as_view(), name='delpaper'),
    
]