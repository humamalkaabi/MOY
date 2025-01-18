from django.urls import path
from django.contrib.auth import views as auth_views
from . import employeedashboard
from . import permissions
from . import registration
from . import profile
from . import views
from . import accountsaffairs
from .logs import personalinfo
from . import search
from .logs import rdd
from .logs import accounts
from . import employeesearch
from . import employeeactivitylog

app_name = 'accounts'


urlpatterns = [

    ################ Control Panel #################
     path('main_control_panel/', views.main_control_panel, name='main_control_panel'),

    path('main_accounts_page/', views.main_accounts_page, name='main_accounts_page'),


     path('mainemployeesearch/', employeesearch.mainemployeesearch, name='mainemployeesearch'),


    # رابط عرض تفاصيل الموظف
    path('employeedashboard/<slug:slug>/', employeedashboard.employeedashboard, name='employeedashboard'),
    path('searchemployeedashboard/<slug:slug>/', employeedashboard.searchemployeedashboard, name='searchemployeedashboard'),



    ################ Permissions #################
    path('mainlistpermissions/', permissions.mainlistpermissions, name='mainlistpermissions'),
    path('list_permissions/', permissions.list_model_permissions, name='list_permissions'),
    path('employees/<int:employee_id>/assign-permissions/', permissions.assign_permissions, name='assign_permissions'),
    path('employees/assign_bulk_permissions/', permissions.assign_bulk_permissions, name='assign_bulk_permissions'),
    path('employees/revoke_bulk_permissions/', permissions.revoke_bulk_permissions, name='revoke_bulk_permissions'),

    #################################### Registration ##############################################
     path('register_new_employee/', registration.register_new_employee, name='register_new_employee'),
     path('generate_sample_upload_employees_csv_csv/', registration.generate_sample_upload_employees_csv_csv, name='generate_sample_upload_employees_csv_csv'),
     path('upload_employees_csv/', registration.upload_employees_csv, name='upload_employees_csv'),
     path('login_view/', registration.login_view, name='login_view'),
    path('password_change/', registration.CustomPasswordChangeView.as_view(), name='password_change'),
    path('logout/', registration.logout_view, name='logout'),



    ################################### Profile #######################
    path('profile/', profile.view_profile, name='view_profile'),



     ### accountsaffairs

path('accounts_main_affiars/', accountsaffairs.accounts_main_affiars, name='accounts_main_affiars'),

    path('employee_list/', accountsaffairs.employee_list, name='employee_list'),
        path('toggle_status/<int:employee_id>/', accountsaffairs.toggle_employee_status, name='toggle_employee_status'),

    path('employee/<str:username>/login-activities/', accountsaffairs.employee_login_activity, name='employee_login_activity'),
#     path('login_activities_list/', accountsaffairs.login_activity_list, name='login_activities_list'),
    path('employee/<slug:slug>/approve/', accountsaffairs.approve_employee, name='approve_employee'),
     
     path('employee_employee_view/', accountsaffairs.employee_employee_view, name='employee_employee_view'),
    path('change-password/<int:employee_id>/', accountsaffairs.change_employee_password, name='change_employee_password'),
    path('export_filtered_employee_csv/', accountsaffairs.export_filtered_employee_csv, name='export_filtered_employee_csv'),



    
        
    path('basic_info_change_log/', personalinfo.basic_info_change_log, name='basic_info_change_log'),
     path('officialtypeslogs/', personalinfo.officialtypeslogs, name='officialtypeslogs'),
    path('emploeeofficialdoc/', personalinfo.emploeeofficialdoc, name='emploeeofficialdoc'),
    path('religionchangelog/', personalinfo.religionchangelog, name='religionchangelog'),
    path('nationalismchangelog/', personalinfo.nationalismchangelog, name='nationalismchangelog'),
    path('additionalinfochangelog/', personalinfo.additionalinfochangelog, name='additionalinfochangelog'),

    path('educationdegreetypechangelog/', rdd.educationdegreetypechangelog, name='educationdegreetypechangelog'),
    path('collegechangelog/', rdd.collegechangelog, name='collegechangelog'),
    path('foreignuniversitychangelog/', rdd.foreignuniversitychangelog, name='foreignuniversitychangelog'),
        path('employeeeducationchangelog/', rdd.employeeeducationchangelog, name='employeeeducationchangelog'),
        
    # path('employeechangelog/', accounts.employeechangelog, name='employeechangelog'),

    




    ############################# Search #######
     path('mainemplpyeesearch/', search.mainemplpyeesearch, name='mainemplpyeesearch'),


     ########################## Resset Password ##################
#       path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset_by_employee_id'),
#     path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
# path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
#         template_name='registration/password_reset_confirm.html'
#     ), name='password_reset_confirm'),    
#     path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('employee_activity_view/', employeeactivitylog.employee_activity_view, name='employee_activity_view'),
    path('employee_activity/<slug:slug>/activity/', employeeactivitylog.employee_activity, name='employee_activity'),
    path('make_superuser/<int:employee_id>/', permissions.make_superuser, name='make_superuser'),

]
