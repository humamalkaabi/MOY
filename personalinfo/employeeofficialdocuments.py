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
from .models import BasicInfo, Employee
from locations.models import Governorate
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BasicInfo
import csv
from django.db.models import Q
from django.shortcuts import render
from .models import Employee
from django.utils.encoding import smart_str
from django.shortcuts import render
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from .models import Employee
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import OfficialDocuments, Official_Documents_Type
from django.db.models import Prefetch
from .forms import OfficialDocumentForm
from hrhub.models.office_position_models import Office

def mainemployeeofficialdocuments(request):
    document_types = Official_Documents_Type.objects.all()

    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    office_query = request.GET.get('office', '')
    has_official_document = request.GET.get('has_official_document', '')
    document_type_query = request.GET.get('document_type', '')
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

    if document_type_query:
        query &= Q(basic_info__employee_official_documents__official_documents_type=document_type_query)
    
    

    # تصفية بناءً على الدائرة والدوائر المرتبطة
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass
    
    if has_official_document:
        if has_official_document.lower() == 'yes':
            query &= Q(basic_info__employee_official_documents__isnull=False)
        elif has_official_document.lower() == 'no':
            query &= Q(basic_info__employee_official_documents__isnull=True)

    employees = Employee.objects.filter(query).distinct()
    employee_count = employees.count()

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

    return render(request, 'personalinfo/official_documents/employee_official_documents/mainemployeeofficialdocuments.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
        'document_types': document_types,
    })

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError


@login_required
@permission_required('personalinfo.can_create_official_documents', raise_exception=True)
def add_official_document(request, slug):
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = OfficialDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.basic_info = basic_info
            document.created_by = request.user

            try:
                document.save()
                # messages.success(request, "تمت إضافة الوثيقة بنجاح!")  # رسالة نجاح جميلة
                return redirect('personalinfo:mainemployeeofficialdocuments')
            except IntegrityError:
                messages.error(request, "⚠️ هذه الوثيقة مضافة مسبقًا لهذا الموظف! الرجاء اختيار نوع آخر.")  # رسالة خطأ جميلة
    
    else:
        form = OfficialDocumentForm()

    return render(request, 'personalinfo/official_documents/employee_official_documents/add_official_document.html', {
        'form': form,
        'basic_info': basic_info,
        'created_by': request.user 
    })


@login_required
def employee_documents(request, slug):
    # استرجاع الموظف باستخدام الـ slug الخاص به
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    # استرجاع جميع الوثائق الخاصة بالموظف
    documents = OfficialDocuments.objects.filter(basic_info=basic_info)
    
    return render(request, 'personalinfo/official_documents/employee_official_documents/employee_documents.html', {'documents': documents, 'basic_info': basic_info})




@login_required
def employee_documents_employee(request, slug):
    # استرجاع الموظف باستخدام الـ slug الخاص به
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع أنواع الوثائق لعرضها في القائمة المنسدلة
    document_types = Official_Documents_Type.objects.all()

    # الحصول على نوع الوثيقة المحدد من طلب GET
    selected_document_type = request.GET.get('document_type', '')

    # تصفية الوثائق الخاصة بالموظف
    documents = OfficialDocuments.objects.filter(basic_info=basic_info)
    if selected_document_type:
        documents = documents.filter(official_documents_type_id=selected_document_type)

    # حساب عدد الوثائق بعد التصفية
    documents_count = documents.count()

    return render(request, 'personalinfo/official_documents/employee/employee_documents_employee.html', {
        'documents': documents,
        'basic_info': basic_info,
        'document_types': document_types,
        'selected_document_type': selected_document_type,
        'documents_count': documents_count,  # عدد الوثائق لعرضه في القائمة الجانبية
    })




@login_required
@permission_required('personalinfo.can_update_official_documents', raise_exception=True)
def edit_official_document(request, slug):
    # الحصول على الوثيقة باستخدام الـ slug
    document = get_object_or_404(OfficialDocuments, slug=slug)

    # إنشاء النموذج مع البيانات الحالية
    if request.method == 'POST':
        form = OfficialDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('personalinfo:employee_documents', slug=document.basic_info.slug)  # إعادة التوجيه إلى صفحة عرض الوثائق الخاصة بالموظف
    else:
        form = OfficialDocumentForm(instance=document)

    return render(request, 'personalinfo/official_documents/employee_official_documents/edit_official_document.html', 
                  {'form': form, 'document': document ,  'created_by': request.user })



@login_required
@permission_required('personalinfo.can_delete_official_documents', raise_exception=True)
def delete_official_document(request, slug):
    
    document = get_object_or_404(OfficialDocuments, slug=slug)
    
    # حذف الوثيقة
    document.delete()
    
    messages.success(request, "تم حذف الوثيقة بنجاح.")
    return redirect('personalinfo:employee_documents', slug=document.basic_info.slug)  # التوجيه إلى صفحة الوثائق الخاصة بالموظف





import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Employee, BasicInfo, OfficialDocuments, Official_Documents_Type, Governorate
from .forms import CSVUploadEmployeeOfficialDocumentForm

def parse_date(date_string):
    """
    تحويل التاريخ إلى الصيغة المطلوبة (YYYY-MM-DD).
    إذا لم يتمكن من التحويل، يعيد None.
    """
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']  # قائمة التنسيقات المحتملة
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None

@login_required
@permission_required('personalinfo.can_create_official_documents', raise_exception=True)
def upload_official_documents_csv(request):
    if request.method == 'POST':
        form = CSVUploadEmployeeOfficialDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # تخطي الصف الأول (عناوين الأعمدة)

                for row in reader:
                    try:
                        emp_username = row[0].strip() if row[0].strip() else None
                        document_type = row[1].strip() if row[1].strip() else None
                        document_id_number = row[2].strip() if row[2].strip() else None
                        issuer_name = row[3].strip() if row[3].strip() else None
                        issuance_date = row[4].strip() if row[4].strip() else None
                        expire_date = row[5].strip() if row[5].strip() else None

                        issuance_date = parse_date(issuance_date) if issuance_date else None
                        expire_date = parse_date(expire_date) if expire_date else None

                        try:
                            emp = Employee.objects.get(username=emp_username)
                            basic_info = emp.basic_info
                        except (Employee.DoesNotExist, BasicInfo.DoesNotExist):
                            messages.error(request, f"الموظف برقم وظيفي {emp_username} غير موجود أو لا يحتوي على BasicInfo.")
                            continue

                        doc_type = Official_Documents_Type.objects.filter(name_in_arabic=document_type).first()
                        if not doc_type:
                            messages.error(request, f"نوع الوثيقة {document_type} غير موجود.")
                            continue

                        issuer = Governorate.objects.filter(name_arabic=issuer_name).first() if issuer_name else None

                        OfficialDocuments.objects.update_or_create(
                            basic_info=basic_info,
                            official_documents_type=doc_type,
                            defaults={
                                'official_documents_id_number': document_id_number,
                                'issuer': issuer,
                                'personal_id_issuance_date': issuance_date,
                                'personal_id_expire_date': expire_date,
                                'created_by': request.user if isinstance(request.user, Employee) else None,
                            }
                        )
                    except Exception as e:
                        messages.error(request, f"خطأ أثناء معالجة السطر {row}: {str(e)}")
                        continue

                messages.success(request, "تم تحميل البيانات بنجاح!")
                return redirect('personalinfo:mainemployeeofficialdocuments')
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء قراءة الملف: {str(e)}")
    else:
        form = CSVUploadEmployeeOfficialDocumentForm()

    return render(request, 'personalinfo/official_documents/employee_official_documents/upload_official_documents_csv.html', {'form': form})



@login_required
def download_sample_official_documents_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="official_documents_sample.csv"'

    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين
    header = [
        'اسم المستخدم (رقم الموظف)', 
        'نوع الوثيقة', 
        'رقم الوثيقة', 
        'جهة الإصدار', 
        'تاريخ الإصدار (YYYY-MM-DD)', 
        'تاريخ الانتهاء (YYYY-MM-DD)'
    ]
    writer.writerow(header)

    # كتابة بيانات عينة
    sample_rows = [
        ['emp123', 'جواز سفر', 'A12345678', 'بغداد', '2023-01-01', '2033-01-01'],
        ['emp456', 'بطاقة هوية', '987654321', 'البصرة', '2022-06-15', '2032-06-15'],
    ]
    writer.writerows(sample_rows)

    return response



@login_required
def export_official_documents_csv(request):
    # استلام القيم من استعلام البحث
    username_query = request.GET.get('username', '')  # اسم المستخدم
    document_type_query = request.GET.get('document_type', '')  # نوع الوثيقة
    has_official_document = request.GET.get('has_official_document', '')  # التحقق إذا كان لديه وثيقة رسمية أم لا

    # جلب جميع الوثائق الرسمية
    official_documents = OfficialDocuments.objects.all()

    # تطبيق الفلاتر بناءً على المدخلات
    if username_query:
        official_documents = official_documents.filter(basic_info__emp_id__username__icontains=username_query)
    if document_type_query:
        official_documents = official_documents.filter(official_documents_type__name_in_arabic__icontains=document_type_query)
    if has_official_document:  # إذا كان هناك شرط للتحقق
        if has_official_document.lower() == 'yes':  # إذا طلب الموظفين الذين لديهم وثائق رسمية
            official_documents = official_documents.filter(basic_info__employee_official_documents__isnull=False)
        elif has_official_document.lower() == 'no':  # إذا طلب الموظفين الذين لا يمتلكون وثائق رسمية
            official_documents = official_documents.filter(basic_info__employee_official_documents__isnull=True)

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="filtered_official_documents.csv"'
    
    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM (Byte Order Mark) لملف CSV

    writer = csv.writer(response)
    
    # كتابة الرأس
    writer.writerow([
        smart_str('الرقم الوظيفي', encoding='utf-8', errors='ignore'),
        smart_str('نوع الوثيقة', encoding='utf-8', errors='ignore'),
        smart_str('رقم الوثيقة', encoding='utf-8', errors='ignore'),
        smart_str('جهة الإصدار', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإصدار', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الانتهاء', encoding='utf-8', errors='ignore'),
        smart_str('قام بإنشاء السجل', encoding='utf-8', errors='ignore'),
    ])

    # كتابة البيانات بعد تطبيق الفلاتر
    for doc in official_documents:
        created_by = doc.created_by.username if doc.created_by else 'غير معروف'
        row = [
            smart_str(doc.basic_info.emp_id.username, encoding='utf-8', errors='ignore') if doc.basic_info else 'غير متوفرة',
            smart_str(doc.official_documents_type.name_in_arabic, encoding='utf-8', errors='ignore') if doc.official_documents_type else 'غير متوفرة',
            doc.official_documents_id_number or 'غير متوفرة',
            doc.issuer.name_arabic if doc.issuer else 'غير متوفرة',
            doc.personal_id_issuance_date.strftime('%d/%m/%Y') if doc.personal_id_issuance_date else 'غير متوفرة',
            doc.personal_id_expire_date.strftime('%d/%m/%Y') if doc.personal_id_expire_date else 'غير متوفرة',
            created_by
        ]
        writer.writerow(row)

    return response
