from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from personalinfo.models import  BasicInfo, BasicInfoChangeLog
from django.core.paginator import Paginator
from rddepartment.models.Education_Degree_Type import EducationDegreeTypeChangeLog



@login_required
def educationdegreetypechangelog(request):
    """
    عرض جميع سجلات تغييرات أنواع الشهادات الدراسية مع دعم البحث والتصفية.
    """
    change_logs = EducationDegreeTypeChangeLog.objects.select_related('education_degree_type', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    degree_name = request.GET.get('degree_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if degree_name:
        change_logs = change_logs.filter(education_degree_type__name_in_arabic__icontains=degree_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/rdd/educationdegreetypechangelog.html', context)



from rddepartment.models.universities_models import CollegeChangeLog, ForeignUniversityChangeLog, IraqiUniversityChangeLog

@login_required
def collegechangelog(request):
    """
    عرض جميع سجلات تغييرات الكليات مع دعم البحث والتصفية.
    """
    change_logs = CollegeChangeLog.objects.select_related('college', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    college_name = request.GET.get('college_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if college_name:
        change_logs = change_logs.filter(college__name_in_arabic__icontains=college_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    return render(request, 'accounts/logs/rdd/collegechangelog.html', context)



@login_required
def foreignuniversitychangelog(request):
    change_logs = ForeignUniversityChangeLog.objects.select_related('foreign_university', 'user').order_by('-timestamp')

    university_name = request.GET.get('university_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if university_name:
        change_logs = change_logs.filter(foreign_university__name_in_english__icontains=university_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    return render(request, 'accounts/logs/rdd/foreignuniversitychangelog.html', context)


@login_required
def iraqiuniversitychangelog(request):
    change_logs = IraqiUniversityChangeLog.objects.select_related('iraqi_university', 'user').order_by('-timestamp')

    university_name = request.GET.get('university_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if university_name:
        change_logs = change_logs.filter(iraqi_university__name_in_arabic__icontains=university_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    return render(request, 'accounts/logs/rdd/iraqiuniversitychangelog.html', context)



from rddepartment.models.employee_education_models import EmployeeEducationChangeLog


@login_required
def employeeeducationchangelog(request):
    """
    عرض جميع سجلات تغييرات الشهادات الأكاديمية للموظفين مع دعم البحث والتصفية.
    """
    change_logs = EmployeeEducationChangeLog.objects.select_related('employee_education', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    employee_name = request.GET.get('employee_name')
    certificate_name = request.GET.get('certificate_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if employee_name:
        change_logs = change_logs.filter(employee_education__basic_info__firstname__icontains=employee_name)
    if certificate_name:
        change_logs = change_logs.filter(employee_education__education_degree_type__name_in_arabic__icontains=certificate_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/rdd/employeeeducationchangelog.html', context)