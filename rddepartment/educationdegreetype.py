from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models.Education_Degree_Type import EducationDegreeType


from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


# Governorate Views


@login_required
def main_education_degree_type(request):
   
    education_degree_types = EducationDegreeType.objects.all()
    education_degree_types_counts = EducationDegreeType.objects.count()
    
    
    context = {
        'education_degree_types': education_degree_types,
        'education_degree_types_counts': education_degree_types_counts
    }

    return render(request, 'rddepartment/education_degree_type/maineducationdegreetype.html', context)




from rddepartment.forms.EducationDegreeTypeForm import EducationDegreeTypeForm

@login_required
@permission_required('rddepartment.can_add_education_degree_type', raise_exception=True)
def add_education_degree_type(request):
    login_user = request.user
    if request.method == 'POST':
        form = EducationDegreeTypeForm(request.POST)
        if form.is_valid():
            education_degree_type = form.save(commit=False)
            education_degree_type.created_by = login_user
            education_degree_type.save()
            messages.success(request, "تمت إضافة نوع الشهادة بنجاح!")
            return redirect('rddepartment:main_education_degree_type')  # عدل هذا المسار حسب ما يناسب مشروعك
    else:
        form = EducationDegreeTypeForm()
    
    return render(request, 'rddepartment/education_degree_type/add_education_degree_type.html', {'form': form})


def education_degree_type_detail(request, slug):
    degree_type = get_object_or_404(EducationDegreeType, slug=slug)
    return render(request, 'rddepartment/education_degree_type//education_degree_type_detail.html', {'degree_type': degree_type})


@login_required
@permission_required('rddepartment.can_update_education_degree_type', raise_exception=True)
def update_education_degree_type(request, slug):
    # جلب الكائن المطلوب تحديثه باستخدام الـ slug
    degree_type = get_object_or_404(EducationDegreeType, slug=slug)
    
    if request.method == 'POST':
        # ملء النموذج بالبيانات المرسلة مع البيانات الحالية
        form = EducationDegreeTypeForm(request.POST, instance=degree_type)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث بيانات نوع الشهادة بنجاح!")
            return redirect('rddepartment:main_education_degree_type')  # عدل هذا المسار حسب ما يناسب مشروعك
    else:
        # ملء النموذج بالبيانات الحالية للكائن
        form = EducationDegreeTypeForm(instance=degree_type)
    
    return render(request, 'rddepartment/education_degree_type/update_education_degree_type_detail.html', {'form': form, 'degree_type': degree_type})

    


@login_required
@permission_required('rddepartment.can_delete_education_degree_type', raise_exception=True)
def delete_education_degree_type(request, slug):
    # التحقق من صلاحيات المستخدم
   
    
    education_degree_type = get_object_or_404(EducationDegreeType, slug=slug)
    
    education_degree_type.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('rddepartment:main_education_degree_type')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

@login_required
def export_education_degree_type_to_csv(request):
    # جلب جميع البيانات من EducationDegreeType
    education_degree_types = EducationDegreeType.objects.all()

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="education_degree_types.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    # كتابة الرأس
    writer.writerow([
        smart_str('ID', encoding='utf-8'),
        smart_str('اسم الشهادة بالعربية', encoding='utf-8'),
        smart_str('اسم الشهادة بالانجليزية', encoding='utf-8'),
        smart_str('الدرجة الوظيفية', encoding='utf-8'),
        smart_str('المرحلة الوظيفية', encoding='utf-8'),
        smart_str('مستوى الشهادة', encoding='utf-8'),
        smart_str('سنوات الترفيع', encoding='utf-8'),
        smart_str('النقطة المتوقفة', encoding='utf-8'),
        smart_str('تأثير الشهادات المضافة', encoding='utf-8'),
        smart_str('سنوات التسريع للشهادة المضافة', encoding='utf-8'),
        smart_str('ملاحظات', encoding='utf-8'),
        smart_str('Slug', encoding='utf-8'),
        smart_str('تاريخ الإنشاء', encoding='utf-8'),
        smart_str('تاريخ التحديث', encoding='utf-8'),
    ])

    # كتابة البيانات
    for degree_type in education_degree_types:
        writer.writerow([
            degree_type.id,
            smart_str(degree_type.name_in_arabic, encoding='utf-8'),
            smart_str(degree_type.name_in_english, encoding='utf-8') if degree_type.name_in_english else 'غير متوفر',
            smart_str(degree_type.grade_number.name if degree_type.grade_number else 'غير متوفر', encoding='utf-8'),
            smart_str(degree_type.step_number.name if degree_type.step_number else 'غير متوفر', encoding='utf-8'),
            degree_type.education_degree_number if degree_type.education_degree_number else 'غير متوفر',
            degree_type.years_effects if degree_type.years_effects else 'غير متوفر',
            degree_type.stop_point if degree_type.stop_point else 'غير متوفر',
            'نعم' if degree_type.has_effect else 'لا',
            degree_type.addtion_years_effects if degree_type.addtion_years_effects else 'غير متوفر',
            smart_str(degree_type.comments, encoding='utf-8') if degree_type.comments else 'غير متوفر',
            smart_str(degree_type.slug, encoding='utf-8'),
            degree_type.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            degree_type.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response
