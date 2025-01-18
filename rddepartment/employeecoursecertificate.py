
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
from personalinfo.models import BasicInfo
from accounts.models import Employee
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
from rddepartment.models.course_certificate_models import CourseCertificateType, CourseCertificateInstitution, EmployeeCourseCertificate
from rddepartment.forms.course_certificate_forms import EmployeeCourseCertificateForm
from hrhub.models.office_position_models import Office


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied





@login_required
def mainemployeecoursecertificate(request):

    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    has_certificate = request.GET.get('has_certificate', '')
    office_query = request.GET.get('office', '')
    course_certificate_type_query = request.GET.get('course_certificate_type', '')  # نوع الشهادة  # استعلام الدائرة الجديدة
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

    if has_certificate:
        if has_certificate.lower() == 'yes':
            query &= Q(basic_info__employee_course_certificate__isnull=False)
        elif has_certificate.lower() == 'no':
            query &= Q(basic_info__employee_course_certificate__isnull=True)
    if course_certificate_type_query:
        query &= Q(basic_info__employee_course_certificate__coursecertificatetype__id=course_certificate_type_query)

    # تصفية بناءً على الدائرة والدوائر المرتبطة
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    employees = Employee.objects.filter(query).distinct()
    course_certificate_types = CourseCertificateType.objects.all()  # جلب أنواع الشهادات


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

    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/main_employeecoursecertificate.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
        'has_certificate': has_certificate,
        'course_certificate_type_query': course_certificate_type_query,
        'course_certificate_types': course_certificate_types,
    })



import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def export_filtered_employee_certificates_csv(request):
    # إنشاء استجابة بصيغة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="filtered_employee_certificates.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM لتوافق Excel مع اللغة العربية

    writer = csv.writer(response)

    # كتابة ترويسة الجدول
    writer.writerow([
        'رقم الموظف',
        'اسم الموظف الكامل',
        'نوع الشهادة',
        'المؤسسة المانحة',
        'رقم كتاب إصدار الشهادة',
        'تاريخ إصدار الشهادة',
        'تاريخ المباشرة بالدورة',
        'تاريخ انتهاء الدورة',
        'مدة الدورة',
        'ملاحظات'
    ])

    # بناء استعلام التصفية بناءً على نفس المعايير الموجودة في mainemployeecoursecertificate
    query = Q()

    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_certificate = request.GET.get('has_certificate', '')
    course_certificate_type_query = request.GET.get('course_certificate_type', '')
    office_query = request.GET.get('office', '')

    if username_query:
        query &= Q(basic_info__emp_id__username__icontains=username_query)
    
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )
    
    if has_certificate:
        if has_certificate.lower() == 'yes':
            query &= Q(basic_info__employee_course_certificate__isnull=False)
        elif has_certificate.lower() == 'no':
            query &= Q(basic_info__employee_course_certificate__isnull=True)
    
    if course_certificate_type_query:
        query &= Q(coursecertificatetype__id=course_certificate_type_query)
    
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    # جلب فقط الشهادات التدريبية للموظفين المتطابقين مع معايير التصفية
    certificates = EmployeeCourseCertificate.objects.filter(query).select_related(
        'basic_info', 'basic_info__emp_id', 'coursecertificatetype', 'name_of_the_institution'
    )

    # كتابة البيانات إلى ملف CSV
    for cert in certificates:
        writer.writerow([
            cert.basic_info.emp_id.username if cert.basic_info and cert.basic_info.emp_id else 'غير متوفر',
            cert.basic_info.get_full_name() if cert.basic_info else 'غير متوفر',
            cert.coursecertificatetype.name_in_arabic if cert.coursecertificatetype else 'غير متوفر',
            cert.name_of_the_institution.name_in_arabic if cert.name_of_the_institution else 'غير متوفر',
            cert.course_number if cert.course_number else 'غير متوفر',
            cert.date_issued if cert.date_issued else 'غير متوفر',
            cert.start_date if cert.start_date else 'غير متوفر',
            cert.end_date if cert.end_date else 'غير متوفر',
            cert.course_duration if cert.course_duration else 'غير متوفر',
            cert.comments if cert.comments else 'غير متوفر',
        ])

    return response

@login_required
@permission_required('hrhub.can_add_employee_course_certificate', raise_exception=True)
def add_employeecoursecertificate(request, slug):

    basic_info = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = EmployeeCourseCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            employeeeducation = form.save(commit=False)
            employeeeducation.basic_info = basic_info  # ربط BasicInfo
            employeeeducation.created_by = request.user  # ربط المستخدم الحالي
            employeeeducation.save()
           
            return redirect('rddepartment:mainemployeecoursecertificate')  # قم بتغيير المسار إلى صفحة النجاح
    else:
        form = EmployeeCourseCertificateForm()
    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/add_employeecoursecertificate.html', {'form': form,
                                                                                         'basic_info': basic_info})



@login_required
def all_employee_certificates(request, slug):
    # الحصول على الموظف بناءً على رقمه
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # الحصول على الشهادات الخاصة بهذا الموظف
    certificates = EmployeeCourseCertificate.objects.filter(basic_info=employee)
    
    # إرجاع البيانات للقالب
    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/all_employee_certificates.html', {
        'employee': employee,
        'certificates': certificates
    })


@login_required
def all_employee_certificates_employee(request, slug):
    # الحصول على الموظف بناءً على رقمه
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # الحصول على الشهادات الخاصة بهذا الموظف
    certificates = EmployeeCourseCertificate.objects.filter(basic_info=employee)
    certificate_types = CourseCertificateType.objects.all()
    selected_type_id = request.GET.get('certificate_type', '')

    if selected_type_id:
        certificates = certificates.filter(coursecertificatetype_id=selected_type_id)
    
    certificates_count = certificates.count()

    
    # إرجاع البيانات للقالب
    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/all_employee_certificates_employee.html', {
        'employee': employee,
        'certificates': certificates,
        'certificate_types': certificate_types,
        'selected_type_id': selected_type_id,
        'certificates_count': certificates_count,
    })




@login_required
@permission_required('hrhub.can_update_employee_course_certificate', raise_exception=True)
def update_employeecoursecertificate(request, slug):
    # الحصول على الشهادة الأكاديمية بناءً على الـ slug
    employeecoursecertificate = get_object_or_404(EmployeeCourseCertificate, slug=slug)

    # إذا كان الطلب من نوع POST، نقوم بتحديث الشهادة
    if request.method == 'POST':
        form = EmployeeCourseCertificateForm(request.POST, request.FILES, instance=employeecoursecertificate)  # نمرر الشهادة الحالية
        if form.is_valid():
            # حفظ التغييرات
            form.save()
            # إعادة التوجيه إلى صفحة عرض تفاصيل الشهادة
            return redirect('rddepartment:all_employee_certificates',  slug=employeecoursecertificate.basic_info.slug)
    else:
        # إذا كان الطلب من نوع GET، نعرض النموذج مع القيم الحالية
        form = EmployeeCourseCertificateForm(instance=employeecoursecertificate)

    # إرجاع القالب مع النموذج
    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/update_employeecoursecertificate.html', {'form': form, 'employeecoursecertificate': employeecoursecertificate})





@login_required
@permission_required('hrhub.can_delete_employee_course_certificate', raise_exception=True)
def delete_employeecoursecertificate(request, slug):
   
    employeecoursecertificate = get_object_or_404(EmployeeCourseCertificate, slug=slug)
    
    employeecoursecertificate.delete()
    
    messages.success(request, "تم حذف نوع البيانات بنجاح.")
    return redirect('rddepartment:mainemployeecoursecertificate')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك





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
from rddepartment.forms.course_certificate_forms import EmployeeCourseCertificateCSVUploadForm

# دالة لتحويل النصوص إلى تاريخ مع دعم عدة تنسيقات
def parse_date(date_string):
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None  # إرجاع None إذا لم يكن التنسيق صحيحًا

@login_required
@permission_required('hrhub.can_add_employee_course_certificate', raise_exception=True)
def upload_employee_course_certificate_csv(request):
    """
    رفع بيانات شهادات الموظفين عبر CSV.
    """
    form = EmployeeCourseCertificateCSVUploadForm()

    if request.method == 'POST':
        form = EmployeeCourseCertificateCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)

            next(reader)  # تخطي الصف الأول (العناوين)

            for row in reader:
                try:
                    # قراءة البيانات من الملف مع السماح بالقيم الفارغة
                    emp_username = row[0].strip() if row[0].strip() else None
                    certificate_type_name = row[1].strip() if len(row) > 1 and row[1].strip() else None
                    institution_name = row[2].strip() if len(row) > 2 and row[2].strip() else None
                    course_number = row[3].strip() if len(row) > 3 and row[3].strip() else None
                    date_issued = parse_date(row[4].strip()) if len(row) > 4 and row[4].strip() else None
                    start_date = parse_date(row[5].strip()) if len(row) > 5 and row[5].strip() else None
                    end_date = parse_date(row[6].strip()) if len(row) > 6 and row[6].strip() else None
                    course_duration = row[7].strip() if len(row) > 7 and row[7].strip() else None
                    certificate_file = row[8].strip() if len(row) > 8 and row[8].strip() else None
                    comments = row[9].strip() if len(row) > 9 and row[9].strip() else None

                    # التحقق من الموظف
                    try:
                        emp = Employee.objects.get(username=emp_username)
                        basic_info = emp.basic_info
                    except Employee.DoesNotExist:
                        messages.error(request, f"الموظف {emp_username} غير موجود.")
                        continue

                    # التحقق من نوع الشهادة
                    certificate_type = CourseCertificateType.objects.filter(name_in_arabic=certificate_type_name).first()
                    if not certificate_type:
                        messages.error(request, f"نوع الشهادة {certificate_type_name} غير موجود.")
                        continue

                    # التحقق من المؤسسة المانحة (يمكن أن تكون فارغة)
                    institution = CourseCertificateInstitution.objects.filter(name_in_arabic=institution_name).first() if institution_name else None

                    # إدخال أو تحديث بيانات الشهادة
                    EmployeeCourseCertificate.objects.update_or_create(
                        basic_info=basic_info,
                        coursecertificatetype=certificate_type,
                        name_of_the_institution=institution,
                        course_number=course_number,
                        date_issued=date_issued,
                        start_date=start_date,
                        end_date=end_date,
                        course_duration=course_duration,
                        certificate_file=certificate_file,
                        comments=comments,
                        created_by=request.user if isinstance(request.user, Employee) else None
                    )

                except Exception as e:
                    messages.error(request, f"حدث خطأ في السطر {row}: {e}")
                    continue

            messages.success(request, "تم تحميل البيانات بنجاح!")
            return redirect('rddepartment:mainemployeecoursecertificate')

    return render(request, 'rddepartment/coursecertificate/employeecoursecertificate/upload_employee_course_certificate_csv.html', {'form': form})