# import datetime
from django.forms import ValidationError
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Employee
from personalinfo.models import BasicInfo
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
import csv
from locations.models import Country, Governorate
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponseForbidden

import io
from django.core.exceptions import PermissionDenied
from rddepartment.models.universities_models import College
from rddepartment.forms.college_forms import CollegeForm
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@login_required
def main_college(request):
   
    colleges = College.objects.all()
    colleges_counts = College.objects.count()
    
    
    context = {
        'colleges': colleges,
        'colleges_counts': colleges_counts
    }

    return render(request, 'rddepartment/college/main_college.html', context)



@login_required
@permission_required('rddepartment.can_add_college', raise_exception=True)
def add_college(request):
   
    login_user = request.user
    if request.method == 'POST':
        form = CollegeForm(request.POST)
        if form.is_valid():
            # إعداد الكائن قبل الحفظ
            college = form.save(commit=False)
            college.created_by = login_user
            college.save()
            messages.success(request, "تمت إضافة نوع الشهادة بنجاح!")
            return redirect('rddepartment:main_college')  # عدّل الرابط إذا لزم الأمر
        else:
            messages.error(request, "حدث خطأ أثناء إضافة الكلية . يرجى المحاولة مرة أخرى.")
    else:
        form = CollegeForm()

    # تمرير النموذج والسياق إلى القالب
    return render(request, 'rddepartment/college/add_college.html', {
        'form': form,
        'login_user': login_user,
        'created_by': request.user,
    })



def college_detail(request, slug):
    college = get_object_or_404(College, slug=slug)
    return render(request, 'rddepartment/college/college_detail.html', {'college': college})


@login_required
@permission_required('rddepartment.can_update_college', raise_exception=True)
def update_college(request, slug):
    # Retrieve the specific instance using the slug
    college = get_object_or_404(College, slug=slug)
    
    if request.method == 'POST':
        form = CollegeForm(request.POST, instance=college)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث  الكلية بنجاح!")
            return redirect('rddepartment:main_college')  # Adjust the URL name as needed
        else:
            messages.error(request, "حدث خطأ أثناء تحديث  الكلية. يرجى المحاولة مرة أخرى.")
    else:
        form = CollegeForm(instance=college)
    
    return render(request, 'rddepartment/college/update_college.html', {
        'form': form,
        'college': college,
        'created_by': request.user,
    })





@login_required
@permission_required('rddepartment.can_delete_college', raise_exception=True)
def delete_college(request, slug):
   
    college = get_object_or_404(College, slug=slug)
    
    college.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('rddepartment:main_college')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك




import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

@login_required
def export_college_to_csv(request):
    # جلب جميع بيانات الكليات
    colleges = College.objects.all()

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="colleges.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    # كتابة الرأس
    writer.writerow([
        smart_str('ID', encoding='utf-8'),
        smart_str('اسم الكلية بالعربية', encoding='utf-8'),
        smart_str('اسم الكلية بالانجليزية', encoding='utf-8'),
        smart_str('Slug', encoding='utf-8'),
        smart_str('تاريخ الإنشاء', encoding='utf-8'),
        smart_str('تاريخ التحديث', encoding='utf-8'),
    ])

    # كتابة البيانات
    for college in colleges:
        writer.writerow([
            college.id,
            smart_str(college.name_in_arabic, encoding='utf-8'),
            smart_str(college.name_in_english, encoding='utf-8'),
            smart_str(college.slug, encoding='utf-8') if college.slug else 'غير متوفر',
            college.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            college.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response
