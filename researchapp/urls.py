from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('contact/',views.contact, name = 'contact'),
    path('people/',views.people, name = 'people'),
    path('research/', views.research, name = 'research'),
    path('logged/',views.login, name = 'homelogged'),
    path('logout/',views.logoutView, name = 'loggedout'),
    path('researchgroup', views.researchgroup, name = 'researchgroup'),
    path('signin', views.signin, name = 'signin'),
#admin
    path('aluser/', views.ListUserView.as_view(), name='aluser'),
    path('alvuser/<int:pk>', views.ALViewUser.as_view(), name='alvuser'),
    path('aeuser/<int:pk>', views.AEditUser.as_view(), name='aeuser'),

#dashboard
    path('index/',views.index, name = 'index'),
    path('listusers/', views.dashboardManageUsers, name= 'listusers'),
    path('dashboard/',views.dashboardView, name = 'dashboard')
]