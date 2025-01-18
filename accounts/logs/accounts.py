from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from personalinfo.models import  BasicInfo, BasicInfoChangeLog
from django.core.paginator import Paginator
from rddepartment.models.Education_Degree_Type import EducationDegreeTypeChangeLog
from accounts.models import EmployeeChangeLog

@login_required
def employeechangelog(request):
    """
    عرض جميع سجلات تغييرات حسابات الموظفين مع دعم البحث والتصفية.
    """
    change_logs = EmployeeChangeLog.objects.select_related('employee', 'changed_by').order_by('-changed_at')

    # تصفية النتائج حسب بيانات البحث
    employee_name = request.GET.get('employee_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if employee_name:
        change_logs = change_logs.filter(employee__username__icontains=employee_name)
    if action:
        change_logs = change_logs.filter(change_type=action)
    if user:
        change_logs = change_logs.filter(changed_by__username__icontains=user)

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/accounts/employeechangelog.html', context)