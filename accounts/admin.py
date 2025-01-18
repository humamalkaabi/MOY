from django.contrib import admin
from .models import Employee, EmployeeChangeLog, EmployeeActivityLog
# Register your models here.


admin.site.register(Employee)
admin.site.register(EmployeeChangeLog)
admin.site.register(EmployeeActivityLog)

