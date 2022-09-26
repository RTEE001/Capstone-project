from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('contact/',views.contact, name = 'contact'),
    path('people/',views.people, name = 'people'),
    path('research/', views.research, name = 'research'),
    path('logged/',views.login1, name = 'loggedin'),
    path('logout/',views.logoutView, name = 'loggedout'),


    path('researchgroup/', views.researchgroup, name = 'researchgroup'),
    path('signin/', views.signin, name = 'signin'),
    path('searchPeopleResult/', views.searchPeopleResult, name = 'searchPeopleResult'),
    path('searchGroupResult/', views.searchGroupsResult,name='searchGroupResult'),
    path('avprofle/<int:pk>', views.AViewProfile.as_view(), name='avprofile'),
    path('avGprofle/<int:pk>', views.AViewGroupProfile.as_view(), name='avGprofile'),



    path('contact_form/', views.CreateContactUs.as_view(), name = 'contact_form'),



    path('papers/', views.filter_papers, name = 'papers'),
    path('reports/', views.reports, name = 'reports'),
    path('papers_pdf/', views.generate_pdf, name = 'paperpdf'),
    path('search_paper/', views.search_paper, name="search_paper"),

    path('upload/', views.upload_paper, name = 'upload'),

    path('search/', views.search, name = 'search'),

#admin
    path('aluser/', views.ListUserView.as_view(), name='aluser'),
    path('alvuser/<int:pk>', views.ALViewUser.as_view(), name='alvuser'),
  
#dashboard
   
    path('listusers/', views.dashboardManageUsers, name= 'listusers'),
    path('dashboard/',views.dashboardView, name = 'dashboard'),
    path('listgroups/', views.dashboardManageGroups, name ='listgroups'),   
    path('aegroup/<int:pk>', views.AEditGroup.as_view(), name='aegroup'),
    path('aeuser/<int:pk>', views.AEditUser.as_view(), name='aeuser'),
    path('addstu/', views.createStudent, name='addstu'),
    path('addGA/', views.createGroupAdmin, name='addGA'),
    path('addUA/', views.createUniAdmin, name='addUA'),
    path('addCA/', views.createCAIRAdmin, name='addCA'),
    path('addR/', views.createResearcher, name='addR'),
    path('createStuUser/', views.create_stuUser, name= 'createStuUser'),
    path('createGAUser/', views.create_grpAdmin, name= 'createGAUser'),
    path('createUAUser/', views.create_uniAdmin, name= 'createUAUser'),
    path('createCAUser/', views.create_CAIRAdmin, name= 'createCAUser'),
    path('createRUser/', views.create_Researcher, name= 'createRUser'),
    path('change_password', views.passwordChange, name='change_password'),
    path('manageusersearch/',views.manageUserFilter, name ='manageusersearch'), 
    path('addUni/', views.addUni, name= 'addUni'),
    path('addUnidetails,', views.addUnidetails, name= 'addUnidetails'),


    path('list_chats/', views.ListMessages.as_view(), name = 'contact_list')

]