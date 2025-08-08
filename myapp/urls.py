from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # if you're using a custom logout view
    path('signup/', views.choose_signup, name='choose_signup'),
    path('signup/employee/', views.employee_signup, name='employee_signup'),
    path('signup/company/', views.company_signup, name='company_signup'),

    # homepage and dashboard URLs
    path('', views.candidate_home, name='candidate_home'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),

    # hr adding form
    path('add-hr/', views.add_hr_view, name='add_hr'),



    # admin urls
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),


    # profile URLs
    path('profile/', views.profile_view, name='profile'),
    path("profile/edit/", views.profile_edit, name="profile_edit"),


]