from django.contrib import admin
from .models import RequestType, EmployeeRequest
# Register your models here.

admin.site.register(RequestType)
admin.site.register(EmployeeRequest)