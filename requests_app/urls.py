from django.urls import path
from . import views

app_name = 'requests_app'  # تأكد من وجود app_name

urlpatterns = [
    path('create_employee_request/<slug:slug>/', views.create_employee_request, name='create_employee_request'),
    path('mainrequests/', views.mainrequests, name='mainrequests'),
     path('employee_requests/<slug:slug>/', views.employee_requests_list, name='employee_requests_list'),  # ✅ إضافة مسار عرض الطلبات

]
