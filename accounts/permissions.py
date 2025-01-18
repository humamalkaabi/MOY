from django.apps import apps
from django.shortcuts import render
# الاستيرادات
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.utils.text import slugify
from unidecode import unidecode
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext as _
from locations.models import Governorate
from django.shortcuts import render, redirect
from django.contrib import messages
from personalinfo.models import BasicInfo
import csv
from .models import Employee
from django.utils.encoding import smart_str
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from .models import Employee
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmployeePermissionForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission  # استيراد Permission


from collections import defaultdict
from django.contrib.contenttypes.models import ContentType


@login_required
def assign_permissions(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = EmployeePermissionForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('accounts:mainlistpermissions')  # إعادة التوجيه إلى قائمة الموظفين
    else:
        form = EmployeePermissionForm(instance=employee)

    permissions = Permission.objects.all().select_related('content_type')
    grouped_permissions = defaultdict(lambda: defaultdict(list))
    app_verbose_names = {}
    model_verbose_names = {}

    for perm in permissions:
        if perm.codename.startswith('add_') or perm.codename.startswith('change_') or perm.codename.startswith('delete_') or perm.codename.startswith('view_'):
            continue

        app_label = perm.content_type.app_label
        model = perm.content_type.model

        if app_label not in app_verbose_names:
            app_config = apps.get_app_config(app_label)
            app_verbose_names[app_label] = app_config.verbose_name

        if model not in model_verbose_names:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            model_class = content_type.model_class()
            model_verbose_names[model] = model_class._meta.verbose_name if model_class else model

        grouped_permissions[app_label][model].append(perm)

    grouped_permissions_with_names = [
        {
            'app_label': app_label,
            'verbose_name': app_verbose_names.get(app_label, app_label),
            'models': [
                {
                    'model': model_verbose_names.get(model, model),
                    'permissions': perms
                }
                for model, perms in models.items()
            ]
        }
        for app_label, models in grouped_permissions.items()
    ]

    # إعداد قائمة التطبيقات
    app_list = [
        {'app_label': app_label, 'verbose_name': app_verbose_names.get(app_label, app_label)}
        for app_label in grouped_permissions.keys()
    ]

    return render(request, 'accounts/permissions/assign_permissions.html', {
        'form': form,
        'employee': employee,
        'grouped_permissions': grouped_permissions_with_names,
        'app_list': app_list,  # إرسال قائمة التطبيقات إلى القالب
    })



from .forms import BulkPermissionForm

def assign_bulk_permissions(request):
    if request.method == 'POST':
        form = BulkPermissionForm(request.POST)
        if form.is_valid():
            selected_permissions = form.cleaned_data['permissions']
            employees = Employee.objects.all()
            for employee in employees:
                employee.user_permissions.add(*selected_permissions)
            return redirect('accounts:mainlistpermissions')
    else:
        form = BulkPermissionForm()

    # تجميع الصلاحيات حسب التطبيقات
    permissions = Permission.objects.exclude(
        codename__startswith=('add_', 'change_', 'delete_', 'view_')
    ).select_related('content_type')

    grouped_permissions = defaultdict(lambda: defaultdict(list))
    app_verbose_names = {}

    for perm in permissions:
        app_label = perm.content_type.app_label
        model = perm.content_type.model

        # الحصول على اسم التطبيق من إعدادات Django
        if app_label not in app_verbose_names:
            app_config = apps.get_app_config(app_label)
            app_verbose_names[app_label] = app_config.verbose_name

        grouped_permissions[app_label][model].append(perm)

    grouped_permissions_with_names = [
        {
            'app_label': app_label,
            'verbose_name': app_verbose_names.get(app_label, app_label),
            'models': [
                {'model': model, 'permissions': perms}
                for model, perms in models.items()
            ]
        }
        for app_label, models in grouped_permissions.items()
    ]

    return render(request, 'accounts/permissions/assign_bulk_permissions.html', {
        'form': form,
        'grouped_permissions': grouped_permissions_with_names
    })


from .forms import BulkRevokePermissionForm

def revoke_bulk_permissions(request):
    if request.method == 'POST':
        form = BulkRevokePermissionForm(request.POST)
        if form.is_valid():
            selected_permissions = form.cleaned_data['permissions']
            employees = Employee.objects.all()
            for employee in employees:
                employee.user_permissions.remove(*selected_permissions)  # إزالة الصلاحيات
            return redirect('accounts:mainlistpermissions')  # إعادة التوجيه بعد النجاح
    else:
        form = BulkRevokePermissionForm()

    # تجميع الصلاحيات حسب التطبيقات
    permissions = Permission.objects.exclude(
        codename__startswith=('add_', 'change_', 'delete_', 'view_')
    ).select_related('content_type')

    grouped_permissions = defaultdict(lambda: defaultdict(list))
    app_verbose_names = {}

    for perm in permissions:
        app_label = perm.content_type.app_label
        model = perm.content_type.model

        if app_label not in app_verbose_names:
            app_config = apps.get_app_config(app_label)
            app_verbose_names[app_label] = app_config.verbose_name

        grouped_permissions[app_label][model].append(perm)

    grouped_permissions_with_names = [
        {
            'app_label': app_label,
            'verbose_name': app_verbose_names.get(app_label, app_label),
            'models': [
                {'model': model, 'permissions': perms}
                for model, perms in models.items()
            ]
        }
        for app_label, models in grouped_permissions.items()
    ]

    return render(request, 'accounts/permissions/revoke_bulk_permissions.html', {
        'form': form,
        'grouped_permissions': grouped_permissions_with_names
    })


def mainlistpermissions(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    results_per_page = request.GET.get('results_per_page', '10')  # القيمة الافتراضية

    # التأكد من صحة results_per_page
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:  # إذا كانت القيمة صفرًا أو أقل
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    # بناء استعلام Q مع شروط مركبة
    query = Q()

    # إضافة شروط إلى الاستعلام
    if username_query:
        query &= Q(username__icontains=username_query)  # شرط AND
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )  # شروط OR
    if has_basicinfo:
        if has_basicinfo.lower() == 'yes':
            query &= Q(basic_info__isnull=False)  # شرط AND
        elif has_basicinfo.lower() == 'no':
            query &= Q(basic_info__isnull=True)  # شرط AND

    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(employees, results_per_page)
    page_number = request.GET.get('page')  # الحصول على رقم الصفحة


    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # عد النتائج
    employee_count = employees.count()

    return render(request, 'accounts/permissions/mainlistpermissions.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
    })



def list_model_permissions(request):
    permissions_dict = {}
    
    for app_config in apps.get_app_configs():
        app_verbose_name = app_config.verbose_name  # اسم التطبيق كما هو محدد في verbose_name
        app_permissions = {}
        
        for model in app_config.get_models():
            meta = getattr(model, '_meta', None)
            # التحقق من وجود صلاحيات مخصصة داخل Meta
            if meta and hasattr(meta, 'permissions') and meta.permissions:
                app_permissions[model._meta.verbose_name] = meta.permissions
        
        # إضافة التطبيق فقط إذا كان يحتوي على صلاحيات مخصصة
        if app_permissions:
            permissions_dict[app_verbose_name] = app_permissions

    context = {
        "permissions_dict": permissions_dict
    }
    return render(request, 'accounts/permissions/permissions_list.html', context)






@login_required
def make_superuser(request, employee_id):
    # العثور على الموظف حسب الـ ID
    employee = get_object_or_404(Employee, id=employee_id)
    
    # تحديث الموظف ليصبح superuser
    employee.is_superuser = True
    employee.is_staff = True  # تأكد من تعيين is_staff أيضا لتمكين الوصول إلى لوحة الإدارة
    employee.save()
    
    # إعادة التوجيه إلى صفحة الموظفين
    return redirect('accounts:mainlistpermissions')
