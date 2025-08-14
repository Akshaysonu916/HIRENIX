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
    path('admin-dashboard/manage-users/', views.manage_users, name='manage_users'),
    path('admin-dashboard/user/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('admin-dashboard/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin-dashboard/jobs/', views.admin_job_list, name='admin_manage_jobs'),
    path('admin-dashboard/jobs/<int:pk>/delete/', views.admin_job_delete, name='admin_job_delete'),


    # profile URLs
    path('profile/', views.profile_view, name='profile'),
    path("profile/edit/", views.profile_edit, name="profile_edit"),



    # job URLs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/new/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('browse-jobs/', views.browse_jobs, name='browse_jobs'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),

    path("jobs/<int:job_id>/apply/", views.apply_for_job, name="apply_for_job"),
    path("jobs/<int:job_id>/applicants/", views.view_applicants, name="view_applicants"),
    path("company/applications/", views.manage_applications, name="manage_applications"),

]