from django.shortcuts import render, get_object_or_404
from .models import Nationalism, NationalismChangeLog

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from accounts.models import Employee
from django.contrib import messages
from .models import Nationalism  # تغيير من Religion إلى Nationalism
from .forms import NationalismForm  # تأكد من أن لديك نموذج NationalismForm
from django.utils.text import slugify
from unidecode import unidecode
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
def nationalism_change_logs(request, slug):
    nationalism = get_object_or_404(Nationalism, slug=slug)
    change_logs = NationalismChangeLog.objects.filter(nationalism=nationalism)
    return render(request, 'personalinfo/nationalism/nationalism_change_logs.html', {'nationalism': nationalism, 'change_logs': change_logs})



# View: عرض القوميات
@login_required
def main_nationalism(request):
   
    
    nationalisms = Nationalism.objects.all()
    nationalism_count = nationalisms.count()
    
    context = {
        'nationalisms': nationalisms,
        'nationalism_count': nationalism_count
    }

    return render(request, 'personalinfo/nationalism/main_nationalism.html', context)




@login_required
def export_nationalism_csv(request):
    # جلب جميع القوميات
    nationalisms = Nationalism.objects.all()

    # إعداد استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="nationalisms.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM (Byte Order Mark) لملف CSV

    writer = csv.writer(response)

    # كتابة الرأس
    writer.writerow([
        smart_str('اسم القومية بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم القومية بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('ملاحظات عن القومية', encoding='utf-8', errors='ignore'),
        smart_str('التاريخ الذي تم فيه الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('التاريخ الذي تم فيه التحديث', encoding='utf-8', errors='ignore'),
        smart_str('قام بإنشاء السجل', encoding='utf-8', errors='ignore'),
        smart_str('سلاج القومية', encoding='utf-8', errors='ignore'),
    ])

    # كتابة البيانات
    for nationalism in nationalisms:
        created_by = nationalism.created_by.username if nationalism.created_by else 'غير معروف'
        
        row = [
            smart_str(nationalism.name_in_arabic, encoding='utf-8', errors='ignore'),
            smart_str(nationalism.name_in_english or 'غير متوفر', encoding='utf-8', errors='ignore'),
            smart_str(nationalism.commennts or 'غير متوفرة', encoding='utf-8', errors='ignore'),
            nationalism.created_at.strftime('%d/%m/%Y %H:%M') if nationalism.created_at else 'غير متوفر',
            nationalism.updated_at.strftime('%d/%m/%Y %H:%M') if nationalism.updated_at else 'غير متوفر',
            created_by,
            nationalism.slug or 'غير متوفر'
        ]

        writer.writerow(row)

    return response

# View: إضافة قومية جديدة
@login_required
@permission_required('personalinfo.can_create_nationalism', raise_exception=True)
def add_nationalism(request):
    
    
    if request.method == 'POST':
        form = NationalismForm(request.POST)
        if form.is_valid():
            nationalism = form.save(commit=False)
            nationalism.created_by = request.user
            nationalism.save()
            messages.success(request, "تم إضافة القومية بنجاح.")
            return redirect('personalinfo:main_nationalism')
    else:
        form = NationalismForm()

    context = {
        'form': form,
        'created_by': request.user
    }
    return render(request, 'personalinfo/nationalism/add_nationalism.html', context)


def nationalism_detail(request, slug):
    nationalism = get_object_or_404(Nationalism, slug=slug)
    employee_count = nationalism.employeenationalism.count() 
    context = {
        'nationalism': nationalism,
        'employee_count': employee_count,
    }
    return render(request, 'personalinfo/nationalism/nationalism_detail.html', context)


# View: تحديث القومية
@login_required
@permission_required('personalinfo.can_update_nationalism', raise_exception=True)
def main_update_nationalism(request, slug):
  
    
    nationalism = get_object_or_404(Nationalism, slug=slug)
    
    if request.method == 'POST':
        form = NationalismForm(request.POST, instance=nationalism)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث القومية بنجاح.")
            return redirect('personalinfo:main_nationalism')
    else:
        form = NationalismForm(instance=nationalism)

    context = {
        'form': form,
        'nationalism': nationalism,
         'created_by': request.user
    }
    return render(request, 'personalinfo/nationalism/update_nationalism.html', context)


# View: حذف القومية
@login_required
@permission_required('personalinfo.can_delete_nationalism', raise_exception=True)
def delete_nationalism(request, slug):
   
    nationalism = get_object_or_404(Nationalism, slug=slug)
    
    nationalism.delete()
    
    messages.success(request, "تم حذف القومية بنجاح.")
    return redirect('personalinfo:main_nationalism')
