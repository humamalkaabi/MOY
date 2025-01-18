from django.shortcuts import render, redirect
from accounts.models import Employee
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from personalinfo.models import BasicInfo
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from rddepartment.models.universities_models import  IraqiUniversity, ForeignUniversity, College
from rddepartment.models.employee_education_models import EmployeeEducation
from rddepartment.models.Education_Degree_Type import EducationDegreeType
from rddepartment.forms.employee_education_form import EmployeeEducationForm, EmployeeEducationCSVUploadForm
from hrhub.models.hr_utilities_models import DutyAssignmentOrder
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
from accounts.models import Employee
from personalinfo.models import BasicInfo
from locations.models import Governorate
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from django.db.models import Q
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.shortcuts import render
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db.models import Exists, OuterRef
from hrhub.models.office_position_models import Office
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@login_required
def main_employeeeducation(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    has_certificate = request.GET.get('has_certificate') 
    certificate_type_query = request.GET.get('certificate_type')
    college_query = request.GET.get('college')
    has_foreign_university = request.GET.get('has_foreign_university')
    has_iraqi_university = request.GET.get('has_iraqi_university') 
    has_addition_certificate = request.GET.get('has_addition_certificate')
    office_query = request.GET.get('office', '')
    results_per_page = request.GET.get('results_per_page', '10')

    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    query = Q()

    if username_query:
        query &= Q(username__icontains=username_query)
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )
    if has_certificate:
        if has_certificate.lower() == 'yes':
            query &= Q(basic_info__employee_education__isnull=False)
        elif has_certificate.lower() == 'no':
            query &= Q(basic_info__employee_education__isnull=True)

    if certificate_type_query:
        query &= Q(basic_info__employee_education__education_degree_type__id=certificate_type_query)
    if gender_query:
        query &= Q(basic_info__gender=gender_query)
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)
    if college_query:
        query &= Q(basic_info__employee_education__college__id=college_query)
    if has_foreign_university:
        if has_foreign_university.lower() == 'yes':
            query &= Q(basic_info__employee_education__foreign_university__isnull=False)
        elif has_foreign_university.lower() == 'no':
            query &= Q(basic_info__employee_education__foreign_university__isnull=True)
    if has_iraqi_university:
        if has_iraqi_university.lower() == 'yes':
            query &= Q(basic_info__employee_education__iraqi_university__isnull=False)
        elif has_iraqi_university.lower() == 'no':
            query &= Q(basic_info__employee_education__iraqi_university__isnull=True)
    if has_addition_certificate:
        if has_addition_certificate.lower() == 'yes':
            query &= Q(basic_info__employee_education__Certificate_Type='adition_cer')
        elif has_addition_certificate.lower() == 'no':
            query &= ~Q(basic_info__employee_education__Certificate_Type='adition_cer')

    root_offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__parent__isnull=True))
    employees = Employee.objects.filter(query)
    education_degree_types = EducationDegreeType.objects.all()
    colleges = College.objects.all()

    paginator = Paginator(employees, results_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    employee_count = employees.count()

    return render(request, 'rddepartment/employeeeducation/main_employeeeducation.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'education_degree_types': education_degree_types,
        'colleges': colleges,
        'offices': root_offices,
    })



@login_required
@permission_required('rddepartment.can_add_employee_education', raise_exception=True)
def add_employeeeducation(request, slug):

    basic_info = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = EmployeeEducationForm(request.POST, request.FILES)
        if form.is_valid():
            employeeeducation = form.save(commit=False)
            employeeeducation.basic_info = basic_info  # ربط BasicInfo
            employeeeducation.created_by = request.user
            employeeeducation.second_approved = True  # ربط المستخدم الحالي
            employeeeducation.save()
           
            return redirect('rddepartment:main_employeeeducation')  # قم بتغيير المسار إلى صفحة النجاح
    else:
        form = EmployeeEducationForm()
    return render(request, 'rddepartment/employeeeducation/add_employeeeducation.html', {'form': form,
                                                                                         'basic_info': basic_info})

@login_required
def employeeeducation_detail(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)
    educations = EmployeeEducation.objects.filter(basic_info=employee)

    return render(request, 'rddepartment/employeeeducation/employeeeducation_detail.html', {'educations': educations, 'employee': employee})



@login_required
def employeeeducation_detail_employee(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)
    educations = EmployeeEducation.objects.filter(basic_info=employee)

    return render(request, 'rddepartment/employeeeducation/employee/employeeeducation_detail_employee.html', {'educations': educations, 'employee': employee})


@login_required
def employee_cer_education_detail(request, slug):
    education = get_object_or_404(EmployeeEducation, slug=slug)
    return render(request, 'rddepartment/employeeeducation/employee_cer_education_detail.html', {'education': education})



@login_required
@permission_required('rddepartment.can_update_employee_education', raise_exception=True)
def update_employeeeducation(request, slug):
    # الحصول على الكائن المطلوب بناءً على الـ slug
    certificate = get_object_or_404(EmployeeEducation, slug=slug)
    
    if request.method == 'POST':
        # إذا كان الطلب POST، قم بملء النموذج بالبيانات المرسلة
        form = EmployeeEducationForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            form.save()
            return redirect('rddepartment:employeeeducation_detail', slug=certificate.slug)  # وجهة إعادة التوجيه بعد التحديث
    else:
        # إذا كان الطلب GET، قم بعرض النموذج مع البيانات الحالية
        form = EmployeeEducationForm(instance=certificate)
    
    return render(request, 'rddepartment/employeeeducation/update_employeeeducation.html', {'form': form, 'certificate': certificate})




@login_required
@permission_required('rddepartment.can_delete_employee_education', raise_exception=True)
def delete_employee_education(request, slug):
    # التحقق من صلاحيات المستخدم
    # if not request.user.has_perm('personalinfo.delete_religion'):
    #     return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    employeeeducation = get_object_or_404(EmployeeEducation, slug=slug)
    
    employeeeducation.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('rddepartment:main_employeeeducation')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك


from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required, permission_required

from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def download_employee_education_sample_csv(request):
    # إعداد الاستجابة بصيغة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="employee_education_sample.csv"'
    
    # دعم UTF-8
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)
    
    # كتابة العناوين
    writer.writerow([
        'الرقم الوظيفي', 'نوع الشهادة', 'الوزارة المانحة', 'طبيعة الشهادة', 
        'نوع الجامعة', 'اسم الجامعة العراقية', 'اسم الجامعة الأجنبية', 
        'الكلية', 'التخصص الدقيق', 'تاريخ اصدار الشهادة', 
        'نوع الامر الصادر بالشهادة', 'رقم الامر الصادر بالشهادة', 
        'تاريخ الامر الصادر بالشهادة', 'تاريخ المباشرة بالدراسة', 
        'تاريخ التخرج', 'تاريخ تنفيذ الامر'
    ])
    
    # كتابة بيانات عينة (اختياري)
   # كتابة بيانات العينة بشكل منفصل
    writer.writerow([
        '12345', 'بكالوريوس', 'وزارة التعليم العالي', 'شهادة مضافة', 
        'جامعة عراقية', 'جامعة بغداد', '', 
        'كلية الهندسة', 'هندسة كهربائية', '2023-01-01', 
        'أمر تعيين', '12345', '2023-02-01', 
        '2022-09-01', '2023-06-30', '2023-07-01'
    ])
    writer.writerow([
        '12345', 'بكالوريوس', 'وزارة التعليم العالي', 'شهادة التعيين', 
        'جامعة عراقية', 'جامعة بغداد', '', 
        'كلية الهندسة', 'هندسة كهربائية', '2023-01-01', 
        'أمر تعيين', '12345', '2023-02-01', 
        '2022-09-01', '2023-06-30', '2023-07-01'
    ])

    
    return response



from rddepartment.forms.employee_education_form import EmployeeEducationCSVUploadForm

def parse_date(date_string):
    """
    تحويل التاريخ إلى صيغة مناسبة (YYYY-MM-DD).
    """
    if not date_string:
        return None
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    return None


import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from rddepartment.models.Education_Degree_Type import EducationDegreeType

import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from  rddepartment.forms.employee_education_form import CSVUploadEmployeeEducationForm



def parse_date(date_string):
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None  # إذا لم يكن التنسيق صحيحًا، سيتم إرجاع None


@login_required
@permission_required('rddepartment.can_add_employee_education', raise_exception=True)
def upload_employee_education_csv(request):
    """
    عرض لرفع بيانات الشهادات الأكاديمية عبر CSV.
    """
    form = CSVUploadEmployeeEducationForm()

    if request.method == 'POST':
        form = CSVUploadEmployeeEducationForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # تخطي الصف الأول (عناوين الأعمدة)

                for row in reader:
                    try:
                        # التحقق من أن الصف يحتوي على القيم الإلزامية فقط
                        if len(row) < 2:
                            messages.error(request, f"السطر {row} لا يحتوي على بيانات كافية (يجب أن يحتوي على رقم الموظف ونوع الشهادة على الأقل).")
                            continue

                        # قراءة البيانات بأمان مع السماح بالقيم الفارغة
                        emp_username = row[0].strip() if row[0] else None
                        degree_type_name = row[1].strip() if row[1] else None
                        ministry_type = row[2].strip() if len(row) > 2 and row[2] else None
                        certificate_nature = row[3].strip() if len(row) > 3 and row[3] else None
                        university_type = row[4].strip() if len(row) > 4 and row[4] else None
                        institution_name = row[5].strip() if len(row) > 5 and row[5] else None
                        iraqi_university_name = row[6].strip() if len(row) > 6 and row[6] else None
                        foreign_university_name = row[7].strip() if len(row) > 7 and row[7] else None
                        college_name = row[8].strip() if len(row) > 8 and row[8] else None
                        certificate_type_detail = row[9].strip() if len(row) > 9 and row[9] else None
                        issuance_date = parse_date(row[10].strip()) if len(row) > 10 and row[10] else None
                        order_type = row[11].strip() if len(row) > 11 and row[11] else None
                        order_number = row[12].strip() if len(row) > 12 and row[12] else None
                        order_date = parse_date(row[13].strip()) if len(row) > 13 and row[13] else None
                        enrollment_date = parse_date(row[14].strip()) if len(row) > 14 and row[14] else None
                        graduation_date = parse_date(row[15].strip()) if len(row) > 15 and row[15] else None
                        effective_date = parse_date(row[16].strip()) if len(row) > 16 and row[16] else None

                        # التحقق من الموظف
                        try:
                            employee = Employee.objects.get(username=emp_username)
                            if not hasattr(employee, 'basic_info'):
                                messages.error(request, f"الموظف {emp_username} لا يحتوي على معلومات أساسية.")
                                continue
                        except Employee.DoesNotExist:
                            messages.error(request, f"الموظف برقم وظيفي {emp_username} غير موجود.")
                            continue

                        # التحقق من نوع الشهادة
                        degree_type = EducationDegreeType.objects.filter(name_in_arabic=degree_type_name).first()
                        if not degree_type:
                            messages.error(request, f"نوع الشهادة {degree_type_name} غير موجود.")
                            continue

                        # التحقق من الجامعة (يمكن أن تكون فارغة)
                        iraqi_university = IraqiUniversity.objects.filter(name_in_arabic=iraqi_university_name).first() if iraqi_university_name else None
                        foreign_university = ForeignUniversity.objects.filter(name_in_english=foreign_university_name).first() if foreign_university_name else None

                        # التحقق من الكلية (يمكن أن تكون فارغة)
                        college = College.objects.filter(name_in_arabic=college_name).first() if college_name else None

                        # التحقق من نوع الأمر الإداري (يمكن أن يكون فارغًا)
                        duty_order = DutyAssignmentOrder.objects.filter(name_in_arabic=order_type).first() if order_type else None

                        # إدخال البيانات مع السماح بالقيم الفارغة
                        EmployeeEducation.objects.update_or_create(
                            basic_info=employee.basic_info,
                            education_degree_type=degree_type,
                            defaults={
                                'certificat_minstery_type': ministry_type,
                                'Certificate_Type': certificate_nature,
                                'university_Type': university_type,
                                'iraqi_university': iraqi_university,
                                'foreign_university': foreign_university,
                                'college': college,
                                'institution_name': institution_name,
                                'Certificate_Type': certificate_type_detail,
                                'date_issued': issuance_date,
                                'duty_assignment_order': duty_order,
                                'duty_assignment_number': order_number,
                                'date_of_administrative_order': order_date,
                                'date_of_enrollment': enrollment_date,
                                'graduation_date': graduation_date,
                                'effective_time': effective_date,
                                'created_by': request.user
                            }
                        )

                    except Exception as e:
                        messages.error(request, f"خطأ أثناء معالجة السطر {row}: {str(e)}")
                        continue

                messages.success(request, "تم تحميل بيانات الشهادات بنجاح!")
                return redirect('rddepartment:main_employeeeducation')

            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء قراءة الملف: {str(e)}")

    return render(request, 'rddepartment/employeeeducation/upload_employee_education_csv.html', {'form': form})


import csv
from django.http import HttpResponse
from django.db.models import Q


import csv
from django.http import HttpResponse
from django.db.models import Q

@login_required
def export_filtered_employee_certificates_csv(request):
    # إنشاء استجابة HTTP بصيغة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="filtered_employee_certificates.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM للتوافق مع Excel

    writer = csv.writer(response)

    # كتابة الصف الرئيسي (Header)
    writer.writerow([
        'رقم الموظف',
        'اسم الموظف الكامل',
        'نوع الشهادة',
        'الوزارة المانحة',
        'اسم المدرسة/الجامعة',
        'نوع الجامعة',
        'الجامعة العراقية',
        'الجامعة الأجنبية',
        'الكلية',
        'التخصص الدقيق',
        'تاريخ إصدار الشهادة',
        'تاريخ التخرج',
        'نوع الأمر',
        'رقم الأمر',
        'تاريخ الأمر',
        'تاريخ المباشرة بالدراسة',
        'تاريخ تنفيذ الأمر',
        'موثق قسم الدراسات',
        'موثق قسم الإدارية',
    ])

    # نسخ استعلام التصفية من `main_employeeeducation`
    query = Q()

    # جلب معايير التصفية من الطلب
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    gender_query = request.GET.get('gender', '')
    has_certificate = request.GET.get('has_certificate')
    certificate_type_query = request.GET.get('certificate_type')
    college_query = request.GET.get('college')
    has_foreign_university = request.GET.get('has_foreign_university')
    has_iraqi_university = request.GET.get('has_iraqi_university')
    has_addition_certificate = request.GET.get('has_addition_certificate')
    office_query = request.GET.get('office', '')

    # بناء استعلام Q بناءً على معايير التصفية
    if username_query:
        query &= Q(username__icontains=username_query)
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )
    if has_certificate:
        if has_certificate.lower() == 'yes':
            query &= Q(basic_info__employee_education__isnull=False)
        elif has_certificate.lower() == 'no':
            query &= Q(basic_info__employee_education__isnull=True)
    if certificate_type_query:
        query &= Q(basic_info__employee_education__education_degree_type__id=certificate_type_query)
    if gender_query:
        query &= Q(basic_info__gender=gender_query)
    if college_query:
        query &= Q(basic_info__employee_education__college__id=college_query)
    if has_foreign_university:
        if has_foreign_university.lower() == 'yes':
            query &= Q(basic_info__employee_education__foreign_university__isnull=False)
        elif has_foreign_university.lower() == 'no':
            query &= Q(basic_info__employee_education__foreign_university__isnull=True)
    if has_iraqi_university:
        if has_iraqi_university.lower() == 'yes':
            query &= Q(basic_info__employee_education__iraqi_university__isnull=False)
        elif has_iraqi_university.lower() == 'no':
            query &= Q(basic_info__employee_education__iraqi_university__isnull=True)
    if has_addition_certificate:
        if has_addition_certificate.lower() == 'yes':
            query &= Q(basic_info__employee_education__Certificate_Type='adition_cer')
        elif has_addition_certificate.lower() == 'no':
            query &= ~Q(basic_info__employee_education__Certificate_Type='adition_cer')

    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    # جلب البيانات بناءً على التصفية
    employees = Employee.objects.filter(query).select_related('basic_info').prefetch_related(
        'basic_info__employee_education__education_degree_type',
        'basic_info__employee_education__iraqi_university',
        'basic_info__employee_education__foreign_university',
        'basic_info__employee_education__college'
    )

    # كتابة البيانات إلى ملف CSV
    for employee in employees:
        basic_info = getattr(employee, 'basic_info', None)
        employee_name = basic_info.get_full_name() if basic_info else 'غير متوفر'

        if basic_info:
            certificates = basic_info.employee_education.all()
            for cert in certificates:
                writer.writerow([
                    employee.username,
                    employee_name,
                    cert.education_degree_type.name_in_arabic if cert.education_degree_type else 'غير متوفر',
                    cert.certificat_minstery_type if cert.certificat_minstery_type else 'غير متوفر',
                    cert.institution_name if cert.institution_name else 'غير متوفر',
                    cert.university_Type if cert.university_Type else 'غير متوفر',
                    cert.iraqi_university.name_in_arabic if cert.iraqi_university else 'غير متوفر',
                    cert.foreign_university.name_in_arabic if cert.foreign_university else 'غير متوفر',
                    cert.college.name_in_arabic if cert.college else 'غير متوفر',
                    cert.Certificate_Type if cert.Certificate_Type else 'غير متوفر',
                    cert.date_issued if cert.date_issued else 'غير متوفر',
                    cert.graduation_date if cert.graduation_date else 'غير متوفر',
                    cert.duty_assignment_order.name_in_arabic if cert.duty_assignment_order else 'غير متوفر',
                    cert.duty_assignment_number if cert.duty_assignment_number else 'غير متوفر',
                    cert.date_of_administrative_order if cert.date_of_administrative_order else 'غير متوفر',
                    cert.date_of_enrollment if cert.date_of_enrollment else 'غير متوفر',
                    cert.effective_time if cert.effective_time else 'غير متوفر',
                    'نعم' if cert.first_approved else 'لا',
                    'نعم' if cert.second_approved else 'لا',
                ])

    return response
