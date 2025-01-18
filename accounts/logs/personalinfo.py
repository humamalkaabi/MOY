from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from personalinfo.models import  BasicInfo, BasicInfoChangeLog
from django.core.paginator import Paginator




@login_required
def basic_info_change_log(request):
    """
    عرض جميع سجلات تغييرات المعلومات الأساسية لجميع الموظفين مع دعم البحث والتصفية.
    """
    change_logs = BasicInfoChangeLog.objects.select_related('basic_info', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    username = request.GET.get('username')
    firstname = request.GET.get('firstname')
    secondname = request.GET.get('secondname')
    thirdname = request.GET.get('thirdname')
    action = request.GET.get('action')

    if username:
        change_logs = change_logs.filter(basic_info__emp_id__username__icontains=username)
    if firstname:
        change_logs = change_logs.filter(basic_info__firstname__icontains=firstname)
    if secondname:
        change_logs = change_logs.filter(basic_info__secondname__icontains=secondname)
    if thirdname:
        change_logs = change_logs.filter(basic_info__thirdname__icontains=thirdname)
    if action:
        change_logs = change_logs.filter(action=action)

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
    }
    return render(request, 'accounts/logs/personalinfo/basic_infochange_log.html', context)


from personalinfo.models import OfficialDocumentsTypeChangeLog, OfficialDocumentsChangeLog

@login_required
def officialtypeslogs(request):
    """
    عرض جميع سجلات تغييرات أنواع الوثائق الرسمية مع دعم البحث والتصفية.
    """
    change_logs = OfficialDocumentsTypeChangeLog.objects.select_related('official_document_type', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    doc_name = request.GET.get('doc_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if doc_name:
        change_logs = change_logs.filter(official_document_type__name_in_arabic__icontains=doc_name)
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
    }
    return render(request, 'accounts/logs/personalinfo/officialtypeslogs.html', context)



@login_required
def emploeeofficialdoc(request):
    """
    عرض جميع سجلات تغييرات الوثائق الرسمية مع دعم البحث والتصفية.
    """
    change_logs = OfficialDocumentsChangeLog.objects.select_related('official_document', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    doc_type = request.GET.get('doc_type')
    doc_number = request.GET.get('doc_number')
    emp_name = request.GET.get('emp_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if doc_type:
        change_logs = change_logs.filter(official_document__official_documents_type__name_in_arabic__icontains=doc_type)
    if doc_number:
        change_logs = change_logs.filter(official_document__official_documents_id_number__icontains=doc_number)
    if emp_name:
        change_logs = change_logs.filter(
            official_document__basic_info__firstname__icontains=emp_name
        )
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
    }
    return render(request, 'accounts/logs/personalinfo/emploeeofficialdoc.html', context)


from personalinfo.models import ReligionChangeLog

@login_required
def religionchangelog(request):
    """
    عرض جميع سجلات تغييرات الديانات مع دعم البحث والتصفية.
    """
    change_logs = ReligionChangeLog.objects.select_related('religion', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    religion_name = request.GET.get('religion_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if religion_name:
        change_logs = change_logs.filter(religion__name_in_arabic__icontains=religion_name)
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
    }
    return render(request, 'accounts/logs/personalinfo/religionchangelog.html', context)

from personalinfo.models import NationalismChangeLog

@login_required
def nationalismchangelog(request):
    """
    عرض جميع سجلات تغييرات القوميات مع دعم البحث والتصفية.
    """
    change_logs = NationalismChangeLog.objects.select_related('nationalism', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    nationalism_name = request.GET.get('nationalism_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if nationalism_name:
        change_logs = change_logs.filter(nationalism__name_in_arabic__icontains=nationalism_name)
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
    }
    return render(request, 'accounts/logs/personalinfo/nationalismchangelog.html', context)


from personalinfo.models import AdditionalInfoChangeLog

@login_required
def additionalinfochangelog(request):
    """
    عرض جميع سجلات تغييرات المعلومات الإضافية مع دعم البحث والتصفية.
    """
    change_logs = AdditionalInfoChangeLog.objects.select_related('additional_info', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    employee_name = request.GET.get('employee_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if employee_name:
        change_logs = change_logs.filter(
            additional_info__basic_info__firstname__icontains=employee_name
        )
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
        'results': change_logs.count
    }
    return render(request, 'accounts/logs/personalinfo/additionalinfochangelog.html', context)