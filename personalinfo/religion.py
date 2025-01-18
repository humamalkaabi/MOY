from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from accounts.models import Employee
from django.contrib import messages
from .models import BasicInfo, Religion
from unidecode import unidecode
from django.utils.text import slugify
from locations.models  import Governorate
import csv
from django.utils.encoding import smart_str

from django.http import HttpResponse
from django.utils.translation import gettext as _
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ReligionForm
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from .models import Religion



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from unidecode import unidecode


@login_required
def mainreligion(request):
   
    
    religions = Religion.objects.all()
    religion_count = religions.count()
    
    context = {
        'religions': religions,
        'religion_count': religion_count
    }

    return render(request, 'personalinfo/religion/mainreligion.html', context)




@login_required
def export_religion_csv(request):
    # جلب جميع الديانات
    religions = Religion.objects.all()

    # إعداد استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="religions.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM (Byte Order Mark) لملف CSV

    writer = csv.writer(response)

    # كتابة الرأس
    writer.writerow([
        smart_str('اسم الديانة بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم الديانة بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('ملاحظات عن الديانة', encoding='utf-8', errors='ignore'),
        smart_str('التاريخ الذي تم فيه الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('التاريخ الذي تم فيه التحديث', encoding='utf-8', errors='ignore'),
        smart_str('قام بإنشاء السجل', encoding='utf-8', errors='ignore'),
        smart_str('مختصر الديانة', encoding='utf-8', errors='ignore'),
    ])

    # كتابة البيانات
    for religion in religions:
        created_by = religion.created_by.username if religion.created_by else 'غير معروف'
        
        row = [
            smart_str(religion.name_in_arabic, encoding='utf-8', errors='ignore'),
            smart_str(religion.name_in_english or 'غير متوفر', encoding='utf-8', errors='ignore'),
            smart_str(religion.commennts or 'غير متوفرة', encoding='utf-8', errors='ignore'),
            religion.created_at.strftime('%d/%m/%Y %H:%M') if religion.created_at else 'غير متوفر',
            religion.updated_at.strftime('%d/%m/%Y %H:%M') if religion.updated_at else 'غير متوفر',
            created_by,
            religion.slug or 'غير متوفر'
        ]

        writer.writerow(row)

    return response


@login_required
@permission_required('personalinfo.can_create_religion', raise_exception=True)
def add_religion(request):
    
    if request.method == 'POST':
        form = ReligionForm(request.POST)
        if form.is_valid():
            religion = form.save(commit=False)  # لا نحفظ بعد لتعديل `created_by`
            religion.created_by = request.user  # تعيين المستخدم الحالي
            religion.save()  # حفظ النموذج
            messages.success(request, "تم إضافة الديانة بنجاح.")
            return redirect('personalinfo:mainreligion')  # استبدلها باسم الصفحة المناسبة لديك
    else:
        form = ReligionForm()
    
    context = {
        'form': form,
        'create_by': request.user,
    }
    return render(request, 'personalinfo/religion/add_religion.html', context)



def religion_detail(request, slug):
    # جلب سجل الديانة باستخدام slug
    religion = get_object_or_404(Religion, slug=slug)
    employee_count = religion.employeereligion.count() 
    context = {
        'religion': religion,
        'employee_count': employee_count,
    }
    return render(request, 'personalinfo/religion/religion_detail.html', context)


@login_required
@permission_required('personalinfo.can_update_religion', raise_exception=True)
def update_religion(request, slug):
   
    religion = get_object_or_404(Religion, slug=slug)
    
    # التحقق إذا كانت الـ POST تحتوي على البيانات لتحديث السجل
    if request.method == 'POST':
        form = ReligionForm(request.POST, instance=religion)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الديانة بنجاح.")
            return redirect('personalinfo:mainreligion')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك
    else:
        form = ReligionForm(instance=religion)

    context = {
        'form': form,
        'religion': religion,
         'create_by': request.user,
    }
    return render(request, 'personalinfo/religion/update_religion.html', context)


@login_required
@permission_required('personalinfo.can_delete_religion', raise_exception=True)
def delete_religion(request, slug):

    religion = get_object_or_404(Religion, slug=slug)
    
    # حذف السجل
    religion.delete()
    
    messages.success(request, "تم حذف الديانة بنجاح.")
    return redirect('personalinfo:mainreligion')  


def export_religions_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="religions.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM للتوافق مع Excel

    writer = csv.writer(response)

    writer.writerow([
        smart_str('اسم الديانة بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم الديانة بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('ملاحظات عن الديانة', encoding='utf-8', errors='ignore'),
        smart_str('مدخل البيانات', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    for religion in Religion.objects.select_related('created_by').all():
        writer.writerow([
            smart_str(religion.name_in_arabic if religion.name_in_arabic else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(religion.name_in_english if religion.name_in_english else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(religion.commennts if religion.commennts else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(religion.created_by.username if religion.created_by else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(religion.created_at, encoding='utf-8', errors='ignore'),
            smart_str(religion.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response
