from django.shortcuts import render, get_object_or_404
from .models import Employee



from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
def employeedashboard(request, slug):
    # جلب الموظف بناءً على slug
    employee = get_object_or_404(Employee, slug=slug)
    basic_info = getattr(employee, 'basic_info', None)
    additional_info = getattr(basic_info, 'additional_info', None) if basic_info else None
    context = {
        'employee': employee,
        'employee': employee,
        'basic_info': basic_info,
        'additional_info': additional_info,
    }
    return render(request, 'accounts/employeedashboard/employeedashboarddetail.html', context)






from django.shortcuts import render, get_object_or_404
from .models import Employee

from hrhub.models.thanks_punishment_absence_models import EmployeeThanks, EmployeePunishment, EmployeeAbsence




def searchemployeedashboard(request, slug):
    # جلب الموظف بناءً على slug
    employee = get_object_or_404(Employee, slug=slug)
    basic_info = getattr(employee, 'basic_info', None)
    additional_info = getattr(basic_info, 'additional_info', None) if basic_info else None

    thanks_count = 0
    if basic_info:
        thanks_count = EmployeeThanks.objects.filter(emp_id_thanks=basic_info).count()

    punishments_count = 0
    if basic_info:
        punishments_count = EmployeePunishment.objects.filter(emp_id_punishment=basic_info).count()
    
    absences_count = 0
    if basic_info:
        absences_count = EmployeeAbsence.objects.filter(emp_id_absence=basic_info).count()

    context = {
        'employee': employee,
        'basic_info': basic_info,
        'additional_info': additional_info,
        'thanks_count': thanks_count,
        'punishments_count': punishments_count,
        'absences_count': absences_count,  # تمرير عدد الغيابات
    }
    return render(request, 'accounts/employeedashboard/searchemployeedashboard.html', context)

