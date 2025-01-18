from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from hrhub.models.staffing_structure_models import PayrollBudgetType, StaffStructerType
from hrhub.forms.staffing_structure_forms import  PayrollBudgetTypeForm, StaffStructerTypeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
def main_payroll_budget(request):
    payroll_budgets = PayrollBudgetType.objects.all()
    context = {'payroll_budgets': payroll_budgets}
    return render(request, 'hrhub/staffing_structure_models/payroll_budget_type/main_payroll_budget.html', context)



@login_required
@permission_required('hrhub.can_add_payroll_budget_type', raise_exception=True)
def add_payroll_budget(request):
    if request.method == 'POST':
        form = PayrollBudgetTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة نوع الموازنة بنجاح!')
            return redirect('hrhub:main_payroll_budget')  # التوجيه إلى صفحة الموازنات
    else:
        form = PayrollBudgetTypeForm()

    return render(request, 'hrhub/staffing_structure_models/payroll_budget_type/add_payroll_budget.html', {'form': form})

@login_required
@permission_required('hrhub.can_update_payroll_budget_type', raise_exception=True)
def update_payroll_budget(request, slug):
    payroll_budget = get_object_or_404(PayrollBudgetType, slug=slug)
    if request.method == 'POST':
        form = PayrollBudgetTypeForm(request.POST, instance=payroll_budget)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث نوع الموازنة بنجاح.")
            return redirect('hrhub:main_payroll_budget')
    else:
        form = PayrollBudgetTypeForm(instance=payroll_budget)
    return render(request, 'hrhub/staffing_structure_models/payroll_budget_type/update_payroll_budget.html', {'form': form})

@login_required
@permission_required('hrhub.can_delete_payroll_budget_type', raise_exception=True)
def delete_payroll_budget(request, slug):
    payroll_budget = get_object_or_404(PayrollBudgetType, slug=slug)
    payroll_budget.delete()
    messages.success(request, "تم حذف نوع الموازنة بنجاح.")
    return redirect('hrhub:main_payroll_budget')




#######################################


@login_required
def main_staff_structer_type(request):
    staff_structers = StaffStructerType.objects.all()
    context = {'staff_structers': staff_structers}
    return render(request, 'hrhub/staffing_structure_models/staff_structer_type/main_staff_structer_type.html', context)


@login_required
@permission_required('hrhub.can_add_staff_structer_type', raise_exception=True)
def add_staff_structer_type(request):
    if request.method == 'POST':
        form = StaffStructerTypeForm(request.POST)
        if form.is_valid():
            staff_structer = form.save(commit=False)
            staff_structer.created_by = request.user  # تعيين المستخدم الحالي
            staff_structer.save()
            messages.success(request, "تم إضافة نوع الملاك بنجاح.")
            return redirect('hrhub:main_staff_structer_type')
    else:
        form = StaffStructerTypeForm()
    return render(request, 'hrhub/staffing_structure_models/staff_structer_type/add_staff_structer_type.html', {'form': form})

@login_required
@permission_required('hrhub.can_update_staff_structer_type', raise_exception=True)
def update_staff_structer_type(request, slug):
    staff_structer = get_object_or_404(StaffStructerType, slug=slug)
    if request.method == 'POST':
        form = StaffStructerTypeForm(request.POST, instance=staff_structer)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث نوع الملاك بنجاح.")
            return redirect('hrhub:main_staff_structer_type')
    else:
        form = StaffStructerTypeForm(instance=staff_structer)
    return render(request, 'hrhub/staffing_structure_models/staff_structer_type/update_staff_structer_type.html', {'form': form})

@login_required
@permission_required('hrhub.can_delete_staff_structer_type', raise_exception=True)
def delete_staff_structer_type(request, slug):
    staff_structer = get_object_or_404(StaffStructerType, slug=slug)
    staff_structer.delete()
    messages.success(request, "تم حذف نوع الملاك بنجاح.")
    return redirect('hrhub:main_staff_structer_type')









# ##################

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.models import Employee
from personalinfo.models import BasicInfo
from django.db.models import Q

@login_required
def main_staff_employee_list(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_staff_kind = request.GET.get('has_staff_kind', '')  # التصفية الجديدة
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    staff_type_query = request.GET.get('staff_type', '')
    payroll_budget_type_query = request.GET.get('payroll_budget_type', '')  # نوع الملاك
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
    if has_staff_kind:
        if has_staff_kind.lower() == 'yes':
            query &= Q(basic_info__employee_staff_kind__isnull=False)  # علاقة غير مباشرة
        elif has_staff_kind.lower() == 'no':
            query &= Q(basic_info__employee_staff_kind__isnull=True)

    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    if staff_type_query:
        query &= Q(basic_info__employee_staff_kind__employee_staff_type__id=staff_type_query)
    
    if payroll_budget_type_query:
        query &= Q(basic_info__employee_staff_kind__employee_staff_type__payroll_budget_type__id=payroll_budget_type_query)

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    staff_types = StaffStructerType.objects.all()
    payroll_budget_types = PayrollBudgetType.objects.all()

    

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

    return render(request, 'hrhub/staffing_structure_models/employee_staff/main_staff_employee_list.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'staff_types': staff_types,
        'payroll_budget_types': payroll_budget_types,
    })



from hrhub.forms.staffing_structure_forms import EmployeeStaffKindForm
from hrhub.models.staffing_structure_models import EmployeeStaffKind



@login_required
@permission_required('hrhub.can_add_employee_staff_kind', raise_exception=True)
def add_employee_staff_kind(request, slug):
    # الحصول على الموظف باستخدام الـ slug
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # التحقق إذا كان النموذج تم إرساله بشكل صحيح
    if request.method == 'POST':
        form = EmployeeStaffKindForm(request.POST, request.FILES)
        if form.is_valid():
            # تعيين الموظف في النموذج
            employee_staff_kind = form.save(commit=False)
            employee_staff_kind.basic_info = employee  # ربط الموظف بالـ EmployeeStaffKind
            employee_staff_kind.save()  # حفظ البيانات
            return redirect('hrhub:main_staff_employee_list')  # إعادة التوجيه بعد الحفظ
    else:
        form = EmployeeStaffKindForm()

    return render(request, 'hrhub/staffing_structure_models/employee_staff/add_employee_staff_kind.html', {'form': form, 'employee': employee})


@login_required
def employee_staff_list(request, slug):
    # جلب الموظف بناءً على الـ slug
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    # جلب جميع الأنواع المرتبطة بهذا الموظف
    staff_kinds = EmployeeStaffKind.objects.filter(basic_info=basic_info)
    
    context = {
        'staff_kinds': staff_kinds,
        'basic_info': basic_info,
    }
    return render(request, 'hrhub/staffing_structure_models/employee_staff/employee_staff_list.html', context)


@login_required
def employee_staff_detail(request, slug):
    # جلب السجل باستخدام slug
    employee_staff_kind = get_object_or_404(EmployeeStaffKind, slug=slug)
    
    context = {
        'employee_staff_kind': employee_staff_kind,
    }
    return render(request, 'hrhub/staffing_structure_models/employee_staff/employee_staff_detail.html', context)


@login_required
@permission_required('hrhub.can_update_employee_staff_kind', raise_exception=True)
def update_employee_staff_kind(request, slug):
    # جلب السجل المطلوب باستخدام slug
    employee_staff_kind = get_object_or_404(EmployeeStaffKind, slug=slug)

    if request.method == 'POST':
        form = EmployeeStaffKindForm(request.POST, request.FILES, instance=employee_staff_kind)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث نوع الملاك بنجاح.")
            # إعادة التوجيه إلى قائمة أنواع الملاك للموظف
            return redirect('hrhub:employee_staff_list', employee_staff_kind.basic_info.slug)
        else:
            messages.error(request, "يرجى تصحيح الأخطاء أدناه.")
    else:
        form = EmployeeStaffKindForm(instance=employee_staff_kind)

    context = {
        'form': form,
        'employee_staff_kind': employee_staff_kind,
    }
    return render(request, 'hrhub/staffing_structure_models/employee_staff/update_employee_staff_kind.html', context)


@login_required
@permission_required('hrhub.can_delete_employee_staff_kind', raise_exception=True)
def delete_employee_staff_kind(request, slug):
    # تحقق من صلاحيات المستخدم
    
    # جلب السجل المطلوب باستخدام الـ slug
    employee_staff_kind = get_object_or_404(EmployeeStaffKind, slug=slug)
    basic_info_slug = employee_staff_kind.basic_info.slug  # لحفظ السجل المرتبط
    
    # حذف السجل
    employee_staff_kind.delete()
    messages.success(request, "تم حذف نوع الملاك بنجاح.")
    
    # إعادة التوجيه إلى قائمة أنواع الملاك الخاصة بالموظف
    return redirect('hrhub:employee_staff_list', slug=basic_info_slug)





import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from hrhub.forms.staffing_structure_forms import EmployeeStaffKindCSVUploadForm

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
@permission_required('hrhub.can_add_employee_staff_kind', raise_exception=True)
def upload_employee_staff_kind_csv(request):
    if request.method == 'POST':
        form = EmployeeStaffKindCSVUploadForm(request.POST, request.FILES)
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
                        staff_type_name = row.get('نوع الملاك', '').strip()
                        staff_order_number = row.get('رقم الأمر الإداري', '').strip()
                        staff_order_date_str = row.get('تاريخ صدور الأمر', '').strip()
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        staff_order_date = parse_date(staff_order_date_str) if staff_order_date_str else None

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not staff_type_name or not staff_order_number:
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

                        # ✅ البحث عن نوع الملاك أو إنشاؤه
                        staff_type, _ = StaffStructerType.objects.get_or_create(
                            name_in_arabic=staff_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ إنشاء slug فريد
                        slug_base = f"{staff_type.name_in_arabic} - {emp_id}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while EmployeeStaffKind.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء سجل EmployeeStaffKind
                        employee_staff_kind = EmployeeStaffKind.objects.create(
                            created_by=request.user,
                            basic_info=basic_info,
                            employee_staff_type=staff_type,
                            employee_staff_type_number=staff_order_number,
                            employee_staff_type_number_date=staff_order_date,
                            comments=comments,
                            slug=unique_slug
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات الموظفين والملاك بنجاح!")
                return redirect('hrhub:main_staff_employee_list')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeStaffKindCSVUploadForm()

    return render(request, 'hrhub/staffing_structure_models/employee_staff/upload_employee_staff_kind_csv.html', {'form': form})
