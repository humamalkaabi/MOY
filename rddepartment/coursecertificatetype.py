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
from rddepartment.forms.course_certificate_forms import CourseCertificateTypeForm
import io

from django.core.exceptions import PermissionDenied
from rddepartment.models.course_certificate_models import CourseCertificateType



###############################################
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@login_required
def main_coursecertificatetype(request):
    # التحقق من صلاحيات المستخدم
    # التحقق من صلاحيات المستخدم
   
    coursecertificatetypes = CourseCertificateType.objects.all()
    
    
    context = {
        'coursecertificatetypes': coursecertificatetypes
    }

    return render(request, 'rddepartment/coursecertificate/coursecertificatetype/main_coursecertificatetype.html', context)



@login_required
@permission_required('rddepartment.can_add_course_certificate_type', raise_exception=True)
def add_coursecertificatetype(request):
    
    
    login_user = request.user
    if request.method == 'POST':
        form = CourseCertificateTypeForm(request.POST)
        if form.is_valid():
            # إعداد الكائن قبل الحفظ
            coursecertificatetype = form.save(commit=False)
            coursecertificatetype.created_by = login_user
            coursecertificatetype.save()
            messages.success(request, "تمت إضافة الجامعة العراقية  بنجاح!")
            return redirect('rddepartment:main_coursecertificatetype')  # عدّل الرابط إذا لزم الأمر
        else:
            messages.error(request, "حدث خطأ أثناء إضافة الجامعة . يرجى المحاولة مرة أخرى.")
    else:
        form = CourseCertificateTypeForm()

    # تمرير النموذج والسياق إلى القالب
    return render(request, 'rddepartment/coursecertificate/coursecertificatetype/add_coursecertificatetype.html', {
        'form': form,
        'login_user': login_user,
    })


@login_required
def coursecertificatetype_detail(request, slug):
    coursecertificatetype = get_object_or_404(CourseCertificateType, slug=slug)
    return render(request, 'rddepartment/coursecertificate/coursecertificatetype/coursecertificatetype_detail.html', {'coursecertificatetype': coursecertificatetype})


@login_required
@permission_required('rddepartment.can_update_course_certificate_type', raise_exception=True)
def update_coursecertificatetype(request, slug):
    # Retrieve the specific instance using the slug
    coursecertificatetype = get_object_or_404(CourseCertificateType, slug=slug)
    
    if request.method == 'POST':
        form = CourseCertificateTypeForm(request.POST, instance=coursecertificatetype)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث  الكلية بنجاح!")
            return redirect('rddepartment:main_coursecertificatetype')  # Adjust the URL name as needed
        else:
            messages.error(request, "حدث خطأ أثناء تحديث  الكلية. يرجى المحاولة مرة أخرى.")
    else:
        form = CourseCertificateTypeForm(instance=coursecertificatetype)
    
    return render(request, 'rddepartment/coursecertificate/coursecertificatetype/update_coursecertificatetype.html', {
        'form': form,
        'coursecertificatetype': coursecertificatetype,
    })





@login_required
@permission_required('rddepartment.can_delete_course_certificate_type', raise_exception=True)
def delete_coursecertificatetype(request, slug):
   
    coursecertificatetype = get_object_or_404(CourseCertificateType, slug=slug)
    
    coursecertificatetype.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('rddepartment:main_coursecertificatetype')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك




####################### Course Certificate Institution ########################

from rddepartment.models.course_certificate_models import CourseCertificateInstitution

from rddepartment.forms.course_certificate_forms import CourseCertificateInstitutionForm




@login_required
def main_coursecertificateinstitutions(request):
    
    
    coursecertificateinstitutions = CourseCertificateInstitution.objects.all()
    
    
    context = {
        'coursecertificateinstitutions': coursecertificateinstitutions
    }

    return render(request, 'rddepartment/coursecertificate/coursecertificateinstitution/main_coursecertificateInstitution.html', context)



@login_required
@permission_required('rddepartment.can_add_course_certificate_institution', raise_exception=True)
def add_coursecertificateinstitutions(request):
   
    login_user = request.user
    if request.method == 'POST':
        form = CourseCertificateInstitutionForm(request.POST)
        if form.is_valid():
            # إعداد الكائن قبل الحفظ
            coursecertificateinstitution = form.save(commit=False)
            coursecertificateinstitution.created_by = login_user
            coursecertificateinstitution.save()
            messages.success(request, "تمت إضافة الجامعة العراقية  بنجاح!")
            return redirect('rddepartment:main_coursecertificateinstitutions')  # عدّل الرابط إذا لزم الأمر
        else:
            messages.error(request, "حدث خطأ أثناء إضافة الجامعة . يرجى المحاولة مرة أخرى.")
    else:
        form = CourseCertificateInstitutionForm()

    # تمرير النموذج والسياق إلى القالب
    return render(request, 'rddepartment/coursecertificate/coursecertificateinstitution/add_coursecertificateInstitution.html', {
        'form': form,
        'login_user': login_user,
    })


@login_required
def coursecertificateinstitution_detail(request, slug):
    coursecertificateinstitution = get_object_or_404(CourseCertificateInstitution, slug=slug)
    return render(request, 'rddepartment/coursecertificate/coursecertificateinstitution/coursecertificateInstitution_detail.html', {'coursecertificateinstitution': coursecertificateinstitution})


@login_required
@permission_required('rddepartment.can_update_course_certificate_institution', raise_exception=True)
def update_coursecertificateinstitution(request, slug):
    # Retrieve the specific instance using the slug
    coursecertificateinstitution = get_object_or_404(CourseCertificateInstitution, slug=slug)
    
    if request.method == 'POST':
        form = CourseCertificateInstitutionForm(request.POST, instance=coursecertificateinstitution)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث  البيانات بنجاح!")
            return redirect('rddepartment:main_coursecertificateinstitutions')  # Adjust the URL name as needed
        else:
            messages.error(request, "حدث خطأ أثناء تحديث  البيانات. يرجى المحاولة مرة أخرى.")
    else:
        form = CourseCertificateInstitutionForm(instance=coursecertificateinstitution)
    
    return render(request, 'rddepartment/coursecertificate/coursecertificateinstitution/update_coursecertificateInstitution.html', {
        'form': form,
        'coursecertificateinstitution': coursecertificateinstitution,
    })





@login_required
@permission_required('rddepartment.can_delete_course_certificate_institution', raise_exception=True)
def delete_coursecertificateinstitution(request, slug):
    
    
    coursecertificateinstitution = get_object_or_404(CourseCertificateInstitution, slug=slug)
    
    coursecertificateinstitution.delete()
    
    messages.success(request, "تم حذف البيانات  بنجاح.")
    return redirect('rddepartment:main_coursecertificateinstitutions')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك




############################# Employee Course Certificate ############################

from rddepartment.models.course_certificate_models import EmployeeCourseCertificate
from rddepartment.forms.course_certificate_forms import EmployeeCourseCertificateForm, EmployeeCourseCertificateCSVUploadForm



import csv
from django.http import HttpResponse

@login_required
def download_sample_employee_course_certificate_csv(request):
    # إعداد الاستجابة ليتم تحميلها كملف CSV مع الترميز المناسب لدعم اللغة العربية
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="employee_course_certificate_sample.csv"'

    # إعداد كاتب CSV مع الترميز المناسب
    response.write('\ufeff'.encode('utf-8-sig'))  # هذا يضمن أن يتم تحميل الملف مع الترميز الصحيح لدعم اللغة العربية
    writer = csv.writer(response)

    # كتابة عناوين الأعمدة (باللغة العربية)
    header = [
        'رقم الموظف', 
        'نوع الشهادة', 
        'اسم المؤسسة المانحة', 
        'رقم كتاب اصدار الشهادة',
        'تاريخ اصدار الشهادة', 
        'تاريخ المباشرة بالدورة', 
        'تاريخ انتهاء الدورة',
        'ملف الشهادة', 
        'مدة الدورة', 
        'الملاحظات'
    ]
    writer.writerow(header)

    # استخراج البيانات من قاعدة البيانات
    employee_course_certificates = EmployeeCourseCertificate.objects.all()

    # كتابة البيانات لكل شهادة دورة
    for certificate in employee_course_certificates:
        row = [
            certificate.basic_info.emp_id if certificate.basic_info else '',
            certificate.coursecertificatetype.name_in_arabic if certificate.coursecertificatetype else '',
            certificate.name_of_the_institution.name_in_arabic if certificate.name_of_the_institution else '',
            certificate.course_number if certificate.course_number else '',
            certificate.date_issued,
            certificate.start_date,
            certificate.end_date,
            certificate.certificate_file.url if certificate.certificate_file else '',
            certificate.course_duration if certificate.course_duration else '',
            certificate.comments if certificate.comments else ''
        ]
        writer.writerow(row)

    return response




import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages

def upload_employee_course_certificate_csv(request):
   
    if request.method == 'POST':
        form = EmployeeCourseCertificateCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)

            next(reader)  # تخطي الصف الأول (العناوين)

            for row in reader:
                try:
                    # قراءة البيانات من الملف
                    emp_username = row[0].strip() if row[0].strip() else None
                    certificate_type_name = row[1].strip() if row[1].strip() else None
                    institution_name = row[2].strip() if row[2].strip() else None
                    course_number = row[3].strip() if row[3].strip() else None
                    date_issued = row[4].strip() if row[4].strip() else None
                    start_date = row[5].strip() if row[5].strip() else None
                    end_date = row[6].strip() if row[6].strip() else None
                    course_duration = row[7].strip() if row[7].strip() else None
                    certificate_file = row[8].strip() if row[8].strip() else None
                    comments = row[9].strip() if row[9].strip() else None

                    # جلب الموظف باستخدام الاسم المستخدم (username)
                    try:
                        emp = Employee.objects.get(username=emp_username)
                        basic_info = emp.basic_info
                    except Employee.DoesNotExist:
                        messages.error(request, f"الموظف {emp_username} غير موجود.")
                        continue

                    # جلب نوع الشهادة
                    certificate_type = CourseCertificateType.objects.filter(name_in_arabic=certificate_type_name).first()
                    if not certificate_type:
                        messages.error(request, f"نوع الشهادة {certificate_type_name} غير موجود.")
                        continue

                    # جلب المؤسسة المانحة
                    institution = CourseCertificateInstitution.objects.filter(name_in_arabic=institution_name).first()
                    if not institution:
                        messages.error(request, f"المؤسسة المانحة {institution_name} غير موجودة.")
                        continue

                    # تحويل التواريخ إلى تنسيق تاريخي
                    date_issued = datetime.strptime(date_issued, '%d/%m/%Y').date() if date_issued else None
                    start_date = datetime.strptime(start_date, '%d/%m/%Y').date() if start_date else None
                    end_date = datetime.strptime(end_date, '%d/%m/%Y').date() if end_date else None

                    # إنشاء أو تحديث EmployeeCourseCertificate
                    employee_course_certificate, created = EmployeeCourseCertificate.objects.update_or_create(
                        basic_info=basic_info,
                        coursecertificatetype=certificate_type,
                        name_of_the_institution=institution,
                        course_number=course_number,
                        date_issued=date_issued,
                        start_date=start_date,
                        end_date=end_date,
                        course_duration=course_duration,
                        certificate_file=certificate_file,  # يمكنك إضافة التعامل مع الملف إذا كان موجودًا
                        comments=comments,
                        created_by=request.user if isinstance(request.user, Employee) else None
                    )

                except Exception as e:
                    messages.error(request, f"حدث خطأ في السطر {row}: {e}")
                    continue

            messages.success(request, "تم تحميل البيانات بنجاح!")
            return redirect('rddepartment:main_employeecoursecertificate')
    else:
        form = EmployeeCourseCertificateCSVUploadForm()

    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/upload_employee_course_certificate_csv.html', {'form': form})


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Prefetch

def main_employeecoursecertificate(request):
    # استعلامات البحث
    query = request.GET.get('search', '').strip()
    firstname = request.GET.get('firstname', '').strip()
    secondname = request.GET.get('secondname', '').strip()
    thirdname = request.GET.get('thirdname', '').strip()
    basic_info_filter = request.GET.get('basic_info_filter', '')
    additional_info_filter = request.GET.get('additional_info_filter', '')
    per_page = int(request.GET.get('per_page', 10))  # عدد العناصر في الصفحة
    coursecertificatetype_filter = request.GET.get('coursecertificatetype', '')  # إضافة تصفية حسب نوع الشهادة

    # استرجاع جميع الموظفين
    employees = Employee.objects.all()

    # تصفية الموظفين بناءً على رقم الوظيفة
    if query:
        employees = employees.filter(username__icontains=query)

    # البحث بالأسماء
    if firstname or secondname or thirdname:
        employees = employees.filter(
            basic_info__firstname__icontains=firstname,
            basic_info__secondname__icontains=secondname,
            basic_info__thirdname__icontains=thirdname
        )

    # تصفية الموظفين بناءً على وجود `basicinfo`
    if basic_info_filter == 'has_info':
        employees = employees.filter(basic_info__isnull=False)
    elif basic_info_filter == 'no_info':
        employees = employees.filter(basic_info__isnull=True)

    # تصفية الموظفين بناءً على وجود `additionalinfo`
    if additional_info_filter == 'has_info':
        employees = employees.filter(basic_info__additional_info__isnull=False)
    elif additional_info_filter == 'no_info':
        employees = employees.filter(basic_info__additional_info__isnull=True)

    # تصفية الموظفين بناءً على `coursecertificatetype` إذا تم تحديده
    if coursecertificatetype_filter:
        employees = employees.filter(
            basic_info__employee_course_certificate__coursecertificatetype__slug=coursecertificatetype_filter
        )

    # إضافة بيانات EmployeeCourseCertificate مرتبة حسب الأحدث
    employees_with_certificates = employees.prefetch_related(
        Prefetch(
            'basic_info__employee_course_certificate',
            queryset=EmployeeCourseCertificate.objects.order_by('-date_issued'),
            to_attr='latest_certificate'  # استخدام هذا لإحضار أحدث شهادة فقط
        )
    )
    employees_count = employees.count()

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(employees_with_certificates, per_page)
    page = request.GET.get('page')

    try:
        employees_page = paginator.page(page)
    except PageNotAnInteger:
        employees_page = paginator.page(1)
    except EmptyPage:
        employees_page = paginator.page(paginator.num_pages)

    context = {
        'employees': employees_page,
        'query': query,
        'firstname': firstname,
        'secondname': secondname,
        'thirdname': thirdname,
        'employees_count': employees_count,
        'basic_info_filter': basic_info_filter,
        'additional_info_filter': additional_info_filter,
        'per_page': per_page,
        'coursecertificatetype_filter': coursecertificatetype_filter,  # تمرير قيمة الفلتر الجديدة
        'certificate_types': CourseCertificateType.objects.all()  # إضافة قائمة بأنواع الشهادات
    }

    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/main_employeecoursecertificate.html', context)



def employeecoursecertificate_detail(request, slug):
    # الحصول على بيانات الشهادة استناداً إلى الـ slug
    employeecoursecertificate = get_object_or_404(EmployeeCourseCertificate, slug=slug)
    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/employeecoursecertificate_detail.html', {'employeecoursecertificate': employeecoursecertificate})


#########################

# def employee_course_certificates(request, slug):
#     # استرجاع الموظف باستخدام الـ slug الخاص به
#     basic_info = get_object_or_404(BasicInfo, slug=slug)

#     # استرجاع جميع الشهادات التدريبية الخاصة بالموظف
#     certificates = EmployeeCourseCertificate.objects.filter(basic_info=basic_info)

#     # تمرير البيانات إلى القالب لعرضها
#     return render(request, 'rddepartment/CourseCertificate/EmployeeCourseCertificate/employee_course_certificates.html', {'certificates': certificates, 'basic_info': basic_info})