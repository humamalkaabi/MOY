from django.shortcuts import render, redirect, get_object_or_404
from personalinfo.models import BasicInfo
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render, get_object_or_404, redirect
from hrhub.models.grade_step_models import EmployeeGrade, EmployeeStep
from hrhub.models.grade_step_upgrade_models import EmployeeGradeStepSettings
# from hrhub.models.grade_step_upgrade_models import EmployeeGradeStepSettings, EmployeeGradeStep

from .forms.Grade_Step_Forms import EmployeeGradeForm

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied



@login_required
def main_employee_grade(request):
   
    
    employee_grades = EmployeeGrade.objects.all()
    
    return render(request, 'hrhub/grade_grad/main_employee_grade.html', {'employee_grades': employee_grades})


@login_required
@permission_required('hrhub.can_add_grade', raise_exception=True)
def employee_grade_create(request):
    
    
    if request.method == 'POST':
        form = EmployeeGradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.created_by = request.user  # تعيين المستخدم الحالي
            grade.save()
            return redirect('hrhub:main_employee_grade')  # استبدل بالمسار المناسب
    else:
        form = EmployeeGradeForm()
    

    return render(request, 'hrhub/grade_grad/employee_grade_create.html', {'form': form})


@login_required
def grade_detail(request, slug):
    grade = get_object_or_404(EmployeeGrade, slug=slug)
    return render(request, 'hrhub/grade_grad/grade_detail.html', {'grade': grade})


@login_required
@permission_required('hrhub.can_update_grade', raise_exception=True)
def update_employee_grade(request, slug):
    grade = get_object_or_404(EmployeeGrade, slug=slug)
    
    
    if request.method == 'POST':
        form = EmployeeGradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            # messages.success(request, "تم تحديث الدرجة بنجاح.")
            return redirect('hrhub:main_employee_grade')
    else:
        form = EmployeeGradeForm(instance=grade)
    
    return render(request, 'hrhub/grade_grad/update_employee_grade.html', {'form': form, 'grade': grade})


@login_required
@permission_required('hrhub.can_delete_grade', raise_exception=True)
def delete_employee_grade(request, slug):
   
    
    grade = get_object_or_404(EmployeeGrade, slug=slug)
    
    grade.delete()
    
   
    return redirect('hrhub:main_employee_grade')


from hrhub.forms.Grade_Step_Forms import EmployeeGradeCSVUploadForm
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify

@login_required
@permission_required('hrhub.can_add_grade', raise_exception=True)
def upload_employee_grades_csv(request):
    if request.method == 'POST':
        form = EmployeeGradeCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # قراءة محتوى الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                # قراءة جميع البيانات في قائمة
                rows = []
                for row in reader:
                    grade_number = row.get('رقم الدرجة', '').strip()
                    name_in_words = row.get('اسم الدرجة كتابة', '').strip()

                    if not grade_number or not name_in_words:
                        messages.error(request, f"رقم الدرجة أو اسمها مفقود في السطر: {row}.")
                        continue

                    rows.append({'grade_number': int(grade_number), 'name_in_words': name_in_words})

                # إدخال الدرجات الوظيفية إلى قاعدة البيانات
                for row in rows:
                    EmployeeGrade.objects.update_or_create(
                        grade_number=row['grade_number'],
                        defaults={
                            'name_in_words': row['name_in_words'],
                            'slug': slugify(unidecode(row['name_in_words']))
                        }
                    )

                messages.success(request, "تم تحميل الدرجات الوظيفية بنجاح!")
                return redirect('hrhub:main_employee_grade')  # استبدل `employee_grades_list` بالمسار الصحيح
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeGradeCSVUploadForm()

    return render(request, 'hrhub/grade_grad/upload_employee_grades_csv.html', {'form': form})


# ######################## Employee Step ########################

# from django.shortcuts import render, get_object_or_404, redirect
# from .models.grade_step_models import EmployeeGrade, EmployeeStep
from .forms.Grade_Step_Forms import EmployeeStepForm

@login_required
def main_employee_step(request):
    employee_steps = EmployeeStep.objects.all()
    return render(request, 'hrhub/grade_step/main_employee_step.html', {'employee_steps': employee_steps})


@login_required
@permission_required('hrhub.can_add_step', raise_exception=True)
def employee_step_create(request):
    if request.method == 'POST':
        form = EmployeeStepForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.created_by = request.user  # تعيين المستخدم الحالي
            grade.save()
            return redirect('hrhub:main_employee_grade')
    else:
        form = EmployeeStepForm()
    return render(request, 'hrhub/grade_step/employee_step_create.html', {'form': form})


@login_required
@permission_required('hrhub.can_update_step', raise_exception=True)
def update_employee_step(request, slug):
    grade = get_object_or_404(EmployeeStep, slug=slug)
    if request.method == 'POST':
        form = EmployeeStepForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            return redirect('hrhub:main_employee_grade')
    else:
        form = EmployeeStepForm(instance=grade)
    return render(request, 'hrhub/grade_step/update_employee_step.html', {'form': form, 'grade': grade})


@login_required
@permission_required('hrhub.can_delete_step', raise_exception=True)
def delete_employee_step(request, slug):
    grade = get_object_or_404(EmployeeStep, slug=slug)
    grade.delete()
    return redirect('hrhub:main_employee_grade')


@login_required
def step_detail(request, slug):
    grade = get_object_or_404(EmployeeStep, slug=slug)
    return render(request, 'hrhub/grade_step/step_detail.html', {'grade': grade})


from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.models import Employee

from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from hrhub.models.office_position_models import Office

@login_required
def main_employee_grade_step(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    office_query = request.GET.get('office', '')  # استعلام الدائرة الجديدة
    results_per_page = request.GET.get('results_per_page', '10')

    # التحقق من نتائج لكل صفحة
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    # بناء الاستعلامات
    query = Q()

    if username_query:
        query &= Q(username__icontains=username_query)
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )
    if has_basicinfo:
        query &= Q(basic_info__isnull=(has_basicinfo.lower() == 'no'))
    if gender_query:
        query &= Q(basic_info__gender=gender_query)
    if has_phone:
        query &= Q(basic_info__phone_number__isnull=(has_phone.lower() == 'no'))

    # تصفية بناءً على الدائرة والدوائر المرتبطة
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    employees = Employee.objects.filter(query).distinct()

    # التقسيم إلى صفحات
    paginator = Paginator(employees, results_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # جلب الوحدات الإدارية الجذرية أو التي لديها مستوى واحد أعلى
    root_offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__parent__isnull=True))

    return render(request, 'hrhub/employee_grade_step/main_employee_grade_step.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
    })

from hrhub.models.grade_step_upgrade_models import EmployeeGradeStep

@login_required
def employee_grade_step_detail(request, slug):
    # الحصول على الموظف بناءً على الـ slug
    employee = get_object_or_404(Employee, basic_info__slug=slug)
    
    # جلب سجل الدرجة الوظيفية المرتبط به، إن وجد
    grade_step = EmployeeGradeStep.objects.filter(basic_info=employee.basic_info).first()

    return render(request, 'hrhub/employee_grade_step/employee_grade_step_detail.html', {
        'employee': employee,
        'grade_step': grade_step
    })

from  hrhub.forms.Grade_Step_Forms import EmployeeGradeStepForm



login_required
def add_employee_grade_step(request, slug):
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = EmployeeGradeStepForm(request.POST, request.FILES)
        if form.is_valid():
            grade_step = form.save(commit=False)
            grade_step.basic_info = basic_info  # ربط بسجل BasicInfo
            grade_step.created_by = request.user
            grade_step.save()
            return redirect('hrhub:employee_grade_step_detail', slug=basic_info.slug)
    else:
        form = EmployeeGradeStepForm()

    return render(request, 'hrhub/employee_grade_step/add_employee_grade_step.html', {'form': form, 'basic_info': basic_info})






from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from hrhub.forms.Grade_Step_Forms import EmployeeGradeStepSettingsForm

@login_required
def view_employee_grade_step_settings(request):
    # جلب السجل الوحيد
    settings = get_object_or_404(EmployeeGradeStepSettings)

    return render(request, 'hrhub/employee_grade_step/view_employee_grade_step_settings.html', {
        'settings': settings
    })


@permission_required('hrhub.can_update_employee_grade_step_settings', raise_exception=True)
def update_employee_grade_step_settings(request):
    settings = get_object_or_404(EmployeeGradeStepSettings)

    if request.method == 'POST':
        form = EmployeeGradeStepSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
           
            return redirect('hrhub:main_employee_grade_step')
    else:
        form = EmployeeGradeStepSettingsForm(instance=settings)

    return render(request, 'hrhub/employee_grade_step/update_employee_grade_step_settings.html', {'form': form})



# from hrhub.forms.Grade_Step_Forms import EmployeeGradeStepForm

# def add_employee_grade_step(request, slug):
#     employee = get_object_or_404(BasicInfo, slug=slug)  # جلب الموظف عبر `slug`
    
#     if request.method == 'POST':
#         form = EmployeeGradeStepForm(request.POST, request.FILES)
#         if form.is_valid():
#             grade_step = form.save(commit=False)
#             grade_step.employee = employee  # ربط الموظف بالسجل الجديد
#             grade_step.save()
#             return redirect('hrhub:main_employee_grade_step')  # تعديل حسب اسم URL المناسب لديك
#     else:
#         form = EmployeeGradeStepForm()

#     return render(request, 'hrhub/employee_grade_step/employee_grade_step_form.html', {'form': form, 'employee': employee})


import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify
from hrhub.forms.Grade_Step_Forms import EmployeeStepCSVUploadForm


@login_required
@permission_required('hrhub.can_add_step', raise_exception=True)
def upload_employee_steps_csv(request):
    if request.method == 'POST':
        form = EmployeeStepCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # قراءة محتوى الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                # قراءة جميع البيانات في قائمة
                rows = []
                for row in reader:
                    grade_number = row.get('رقم الدرجة', '').strip()
                    step_number = row.get('رقم المرحلة', '').strip()
                    name_in_words = row.get('اسم المرحلة كتابة', '').strip()

                    if not grade_number or not step_number or not name_in_words:
                        messages.error(request, f"بيانات مفقودة في السطر: {row}.")
                        continue

                    rows.append({'grade_number': int(grade_number), 'step_number': int(step_number), 'name_in_words': name_in_words})

                # التحقق من وجود الدرجات الوظيفية وإنشائها إن لم تكن موجودة
                for row in rows:
                    EmployeeGrade.objects.get_or_create(grade_number=row['grade_number'])

                # إدخال المراحل الوظيفية إلى قاعدة البيانات
                for row in rows:
                    grade = EmployeeGrade.objects.filter(grade_number=row['grade_number']).first()
                    if grade:
                        EmployeeStep.objects.update_or_create(
                            grade_number=grade,
                            step_number=row['step_number'],
                            defaults={
                                'name_in_words': row['name_in_words'],
                                'slug': slugify(unidecode(f"{grade.grade_number}-{row['step_number']}-{row['name_in_words']}"))
                            }
                        )

                messages.success(request, "تم تحميل المراحل الوظيفية بنجاح!")
                return redirect('hrhub:main_employee_step')  # استبدل `employee_steps_list` بالمسار الصحيح
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeStepCSVUploadForm()

    return render(request, 'hrhub/grade_step/upload_employee_steps_csv.html', {'form': form})
