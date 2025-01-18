from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



app_name = 'core' 

urlpatterns = [

    path('sucess_link/',views.sucess_link, name='sucess_link'),

    path('', views.main_page, name='main_page'),
    
    path('create_or_update_main_about_us/',views.create_or_update_main_about_us, name='main_about_us_create_or_update'),
    path('view_main_about_us/', views.view_main_about_us, name='view_main_about_us'),
     path('create_or_update_logo/', views.create_or_update_logo, name='create_or_update_logo'),
     path('logo_view/', views.logo_view, name='logo_view'),


    # path('', views.main_page, name='main_page'),
    
    # path('create_or_update_main_about_us/',views.create_or_update_main_about_us, name='main_about_us_create_or_update'),
    # path('view_main_about_us/', views.view_main_about_us, name='view_main_about_us'),
    #  path('create_or_update_logo/', views.create_or_update_logo, name='create_or_update_logo'),
    #  path('logo/view/', views.logo_view, name='logo_view'),



    # path('', views.main_page, name='main_page'),
    # path('create_or_update_basic_info/', views.create_or_update_basic_info, name='create_or_update_basic_info'),
    
   
]
