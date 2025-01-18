from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from hrhub.models.central_financial_allocations_models  import CentralFinancialAllocations, CentralFinancialAllocationsType
from hrhub.forms.centralfinancialallocationstypeform import CentralFinancialAllocationsForm, CentralFinancialAllocationsTypeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied



@login_required
def main_central_financial_allocations(request):
    allocations = CentralFinancialAllocationsType.objects.all()
    context = {'allocations': allocations,
               'allocations_count': allocations.count}
    return render(request, 'hrhub/central_allocation/central_types/main_allocations.html', context)

@login_required
@permission_required('hrhub.can_add_central_financial_allocations_type', raise_exception=True)
def add_central_financial_allocation(request):
    if request.method == 'POST':
        form = CentralFinancialAllocationsTypeForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            # allocation.created_by = request.user.employee  # تعيين المستخدم الحالي
            allocation.save()
            messages.success(request, "تم إضافة المخصص المالي بنجاح.")
            return redirect('hrhub:main_central_financial_allocations')
    else:
        form = CentralFinancialAllocationsTypeForm()
    return render(request, 'hrhub/central_allocation/central_types/add_allocation.html', {'form': form})

@login_required
@permission_required('hrhub.can_update_central_financial_allocations_type', raise_exception=True)
def update_central_financial_allocation(request, slug):
    allocation = get_object_or_404(CentralFinancialAllocationsType, slug=slug)
    if request.method == 'POST':
        form = CentralFinancialAllocationsTypeForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل المخصص المالي بنجاح.")
            return redirect('hrhub:main_central_financial_allocations')
    else:
        form = CentralFinancialAllocationsTypeForm(instance=allocation)
    return render(request, 'hrhub/central_allocation/central_types/update_allocation.html', {'form': form})

@login_required
@permission_required('hrhub.can_delete_central_financial_allocations_type', raise_exception=True)
def delete_central_financial_allocation(request, slug):
    allocation = get_object_or_404(CentralFinancialAllocationsType, slug=slug)
    allocation.delete()
    messages.success(request, "تم حذف المخصص المالي بنجاح.")
    return redirect('hrhub:main_central_financial_allocations')



########## Employee


from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from accounts.models import Employee
from personalinfo.models import BasicInfo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

@login_required
def central_alloc_employee_list(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_allocations = request.GET.get('has_allocations', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    allocation_type_id = request.GET.get('allocation_type', '')
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
    if has_allocations:
        if has_allocations.lower() == 'yes':
            query &= Q(basic_info__allocations__isnull=False)
        elif has_allocations.lower() == 'no':
            query &= Q(basic_info__allocations__isnull=True)

    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)
    if allocation_type_id:
        query &= Q(basic_info__allocations__centralfinancialallocationstype__id=allocation_type_id)

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    allocation_types = CentralFinancialAllocationsType.objects.all()
    

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

    return render(request, 'hrhub/central_allocation/central_employee/central_alloc_employee_list.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'allocation_types': allocation_types,
    })






@login_required
@permission_required('hrhub.can_add_central_financial_allocations', raise_exception=True)
def add_financial_allocations(request, slug):
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = CentralFinancialAllocationsForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.basic_info = basic_info 
            allocation.save()
            return redirect('hrhub:central_alloc_employee_list')  # استبدل 'success' برابط الصفحة المطلوبة بعد الحفظ
    else:
        form = CentralFinancialAllocationsForm()
    
    return render(request, 'hrhub/central_allocation/central_employee/add_financial_allocations.html', {'form': form})




from hrhub.models.central_financial_allocations_models import CentralFinancialAllocations
from hrhub.models.employee_job_title_models import EmployeeJobTitle

from django.shortcuts import render, get_object_or_404
from hrhub.models.office_position_models import EmployeeOfficePosition


@login_required
def employee_allocations(request, slug):
    # جلب بيانات الموظف
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب المخصصات المالية المرتبطة بالموظف
    allocations = CentralFinancialAllocations.objects.filter(basic_info=employee)

    # جلب سجل EmployeeJobTitle المرتبط بالموظف
    employee_job_title_record = EmployeeJobTitle.objects.filter(basic_info=employee).order_by('-employee_job_title_date').first()
    current_job_title = employee_job_title_record.employee_job_title if employee_job_title_record else None

    # جلب بيانات المكتب والمنصب الوظيفي الحالي
    employee_office_position = EmployeeOfficePosition.objects.filter(
        basic_info=employee, status='ongoing'  # تأكد من اختيار الحالة "مستمر"
    ).order_by('-start_date').first()  # اختيار أحدث سجل
    
    current_office = employee_office_position.office if employee_office_position else None
    current_position = employee_office_position.position if employee_office_position else None

    return render(request, 'hrhub/central_allocation/central_employee/employee_allocations.html', {
        'employee': employee,
        'allocations': allocations,
        'current_job_title': current_job_title,
        'current_office': current_office,
        'current_position': current_position,
    })




def central_financial_allocations_detail(request, slug):
    allocation = get_object_or_404(CentralFinancialAllocations, slug=slug)
    return render(request, 'hrhub/central_allocation/central_employee/allocations_detail.html', {'allocation': allocation})


@login_required
@permission_required('hrhub.can_update_central_financial_allocations', raise_exception=True)
def update_financial_allocation(request, slug):
  
    
    # جلب المخصص المالي باستخدام الـ slug
    allocation = get_object_or_404(CentralFinancialAllocations, slug=slug)
    
    if request.method == 'POST':
        form = CentralFinancialAllocationsForm(request.POST, instance=allocation)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.created_by = request.user  # تحديث المستخدم الذي قام بالتعديل
            allocation.save()
            messages.success(request, "تم تحديث المخصص المالي بنجاح.")
            return redirect('hrhub:employee_allocations', allocation.basic_info.slug)  # تعديل الرابط حسب الحاجة
    else:
        form = CentralFinancialAllocationsForm(instance=allocation)
    
    context = {
        'form': form,
        'allocation': allocation,
    }
    return render(request, 'hrhub/central_allocation/central_employee/update_financial_allocation.html', context)



@login_required
@permission_required('hrhub.can_delete_central_financial_allocations', raise_exception=True)
def delete_financial_allocation(request, slug):
    
    # جلب المخصص المالي باستخدام الـ slug
    allocation = get_object_or_404(CentralFinancialAllocations, slug=slug)
    
    # حذف المخصص
    allocation.delete()
    messages.success(request, "تم حذف المخصص المالي بنجاح.")
    return redirect('hrhub:central_alloc_employee_list')  # تعديل الرابط حسب الحاجة




import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from hrhub.forms.centralfinancialallocationstypeform import FinancialAllocationsCSVUploadForm
from locations.models import Governorate

# ✅ دالة لتحويل صيغ التاريخ المختلفة إلى YYYY-MM-DD
def parse_date(date_string):
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None


# ✅ دالة لتحويل صيغ التاريخ المختلفة إلى YYYY-MM-DD
def parse_date(date_string):
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None

@login_required
@permission_required('hrhub.can_add_central_financial_allocations', raise_exception=True)
def upload_financial_allocations_csv(request):
    if request.method == 'POST':
        form = FinancialAllocationsCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # قراءة الملف وتحويله إلى قائمة
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                for row in reader:
                    try:
                        # ✅ قراءة البيانات وتحويل القيم
                        emp_id = row.get('الرقم الوظيفي', '').strip()
                        allocation_type_name = row.get('نوع المخصصات', '').strip()
                        ratio = row.get('نسبة المخصصات رقما', '').strip() or None
                        word_ratio = row.get('نسبة المخصصات كتابة', '').strip() or None
                        order_number = row.get('الأمر الصادر', '').strip()
                        order_time_str = row.get('تاريخ صدور الأمر', '').strip()
                        effective_time_str = row.get('تاريخ تنفيذ الأمر', '').strip()
                        serial_number = row.get('رقم السيريال الخاص بالكومبيوتر', '').strip()
                        mac_number = row.get('رقم mac_namber', '').strip()
                        residency_name = row.get('محافظة سكن الموظف', '').strip()
                        address = row.get('عنوان سكن الموظف', '').strip()
                        vechile_name = row.get('اسم العجلة', '').strip()
                        vechile_number = row.get('رقم العجلة', '').strip()
                        vechile_line = row.get('صفة الخطورة ومكان الخط', '').strip()
                        healthy_cen = row.get('نوع المخصصات الصحية', '').strip()
                        name_prevois = row.get('اسم البديل السابق', '').strip()
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        order_time = parse_date(order_time_str) if order_time_str else None
                        effective_time = parse_date(effective_time_str) if effective_time_str else None

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not allocation_type_name or not order_number:
                            messages.error(request, f"بيانات مفقودة أو تنسيق تاريخ غير صحيح في السطر: {row}.")
                            continue

                        # ✅ البحث عن الموظف
                        employee = Employee.objects.filter(username=emp_id).first()
                        if not employee:
                            messages.error(request, f"الموظف برقم {emp_id} غير موجود في النظام.")
                            continue

                        # ✅ البحث عن BasicInfo للموظف
                        basic_info = BasicInfo.objects.filter(emp_id=employee).first()
                        if not basic_info:
                            messages.error(request, f"لم يتم العثور على بيانات الموظف الأساسية للرقم الوظيفي {emp_id}.")
                            continue

                        # ✅ البحث عن نوع المخصصات أو إنشاؤه
                        allocation_type, _ = CentralFinancialAllocationsType.objects.get_or_create(
                            name_in_arabic=allocation_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ البحث عن محافظة السكن (تم تعديل البحث ليستخدم name_arabic)
                        residency = Governorate.objects.filter(name_arabic=residency_name).first() if residency_name else None

                        # ✅ إنشاء slug فريد
                        slug_base = f"{allocation_type.name_in_arabic} - {emp_id}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while CentralFinancialAllocations.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء سجل CentralFinancialAllocations
                        financial_allocation = CentralFinancialAllocations.objects.create(
                            created_by=request.user,
                            basic_info=basic_info,
                            centralfinancialallocationstype=allocation_type,
                            order_number=order_number,
                            order_time=order_time,
                            effective_time=effective_time,
                            serial_namber=serial_number,
                            mac_namber=mac_number,
                            residency=residency,
                            address=address,
                            vechile_name=vechile_name,
                            vechile_number=vechile_number,
                            vechile_line=vechile_line,
                            healthy_cen=healthy_cen,
                            name_prevois=name_prevois,
                            comments=comments,
                            slug=unique_slug
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات المخصصات المالية بنجاح!")
                return redirect('hrhub:central_alloc_employee_list')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = FinancialAllocationsCSVUploadForm()

    return render(request, 'hrhub/central_allocation/central_employee/upload_financial_allocations_csv.html', {'form': form})
