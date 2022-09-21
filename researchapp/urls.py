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
#admin
    path('aluser/', views.ListUserView.as_view(), name='aluser'),
    path('alvuser/<int:pk>', views.ALViewUser.as_view(), name='alvuser'),
    

#dashboard
    path('index/',views.index, name = 'index'),
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
   
path('manageusersearch/',views.manageUserFilter, name ='manageusersearch'), 
   path('addUni/', views.addUni, name= 'addUni'),
   path('addUnidetails,', views.addUnidetails, name= 'addUnidetails')

]