from django.shortcuts import render, get_object_or_404
from personalinfo.models import BasicInfo
from hrhub.models.employee_leave_models import LeaveBalance, LeaveType, LeaveRequest


from personalinfo.models import BasicInfo
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from  accounts.models import Employee
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from hrhub.forms.leave_forms import LeaveTypeForm, LeaveRequestForm


@login_required
def main_leave_type(request):
    leave_types = LeaveType.objects.all()
    
    context = {
        'leave_types': leave_types
    }

    return render(request, 'hrhub/leave/leave_type/main_leave_type.html', context)

from django.contrib.auth.decorators import login_required

@login_required
@permission_required('hrhub.can_add_leave_type', raise_exception=True)
def add_leave_type(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            leave_type = form.save(commit=False)
            leave_type.created_by = request.user  # ربط بـ login user
            leave_type.save()
            return redirect('hrhub:main_leave_type')  # تعديل URL حسب الحاجة
    else:
        form = LeaveTypeForm()
    return render(request, 'hrhub/leave/leave_type/add_leave_type.html', {'form': form})




@login_required
def leave_type_detail(request, slug):
    leave_type = get_object_or_404(LeaveType, slug=slug)

    context = {
        'leave_type': leave_type
    }
    return render(request, 'hrhub/leave/leave_type/leave_type_detail.html', context)



@login_required
@permission_required('hrhub.can_update_leave_type', raise_exception=True)
def update_leave_type(request, slug):
    leave_type = get_object_or_404(LeaveType, slug=slug)
    
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            leave_type = form.save(commit=False)
            leave_type.created_by = request.user  # تحديث المستخدم الذي قام بالتعديل
            leave_type.save()
            messages.success(request, "تم تحديث نوع الإجازة بنجاح.")
            return redirect('hrhub:main_leave_type')  # تعديل الرابط حسب الحاجة
    else:
        form = LeaveTypeForm(instance=leave_type)
    
    context = {
        'form': form,
        'leave_type': leave_type
    }
    return render(request, 'hrhub/leave/leave_type/update_leave_type.html', context)



@login_required
@permission_required('hrhub.can_delete_leave_type', raise_exception=True)
def delete_leave_type(request, slug):
    if not request.user.has_perm('hrhub.delete_leavetype'):
        return HttpResponseForbidden("ليس لديك الصلاحية لحذف نوع الإجازة.")
    
    leave_type = get_object_or_404(LeaveType, slug=slug)
    leave_type.delete()
    messages.success(request, "تم حذف نوع الإجازة بنجاح.")
    return redirect('hrhub:main_leave_type')


############ LeaveBalance  ###############


@login_required
def main_leave_balance(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    has_leave_balance = request.GET.get('has_leave_balance', '')
    leave_type_query = request.GET.get('leave_type', '')
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
    if has_leave_balance:
        if has_leave_balance.lower() == 'yes':
            query &= Q(basic_info__employee_leave_balances__isnull=False)
        elif has_leave_balance.lower() == 'no':
            query &= Q(basic_info__employee_leave_balances__isnull=True)

    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    if leave_type_query:
        query &= Q(basic_info__employee_leave_balances__leave_type__id=leave_type_query)


    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query).distinct()
    leave_types = LeaveType.objects.all()
    

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

    return render(request, 'hrhub/leave/leavebalance/main_leave_balance.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'leave_types': leave_types,  # تمرير أنواع الإجازات إلى القالب
    })


from django.db import IntegrityError
from hrhub.forms.leave_forms import LeaveBalanceForm

@login_required
@permission_required('hrhub.can_add_leave_balance', raise_exception=True)
def create_leave_balance(request, slug):
    # محاولة الحصول على الموظف باستخدام الـ slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = LeaveBalanceForm(request.POST)
        if form.is_valid():
            leave_balance = form.save(commit=False)
            leave_balance.employee = employee  # تعيين الموظف بناءً على الـ slug

            try:
                leave_balance.save()  # حفظ رصيد الإجازة
                messages.success(request, "تم إضافة رصيد الإجازة بنجاح!")  # إشعار النجاح
                return redirect('hrhub:main_leave_balance')  # إعادة التوجيه إلى صفحة الأرصدة
            except IntegrityError:
                # إذا تم رفع الخطأ بسبب القيد الفريد
                messages.error(request, "لا يمكن إضافة رصيد إجازة لهذا الموظف ونوع الإجازة، لأنهم موجودون بالفعل!")  # إشعار بالخطأ
                return redirect('hrhub:create_leave_balance', slug=slug)  # إعادة التوجيه إلى نفس الصفحة
    else:
        form = LeaveBalanceForm()

    return render(request, 'hrhub/leave/leavebalance/create_leave_balance.html', {'form': form, 'employee': employee})


@login_required
def employee_leave_balances(request, slug):
    # جلب الموظف باستخدام الـ slug الخاص به
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # جلب جميع أرصدة الإجازات الخاصة بالموظف
    leave_balances = LeaveBalance.objects.filter(employee=employee)
    
    context = {
        'employee': employee,
        'leave_balances': leave_balances
    }
    return render(request, 'hrhub/leave/leavebalance/employee_leave_balances.html', context)

@login_required
@permission_required('hrhub.can_update_leave_balance', raise_exception=True)
def update_leave_balance_view(request, slug):
    leave_balance = get_object_or_404(LeaveBalance, slug=slug)

    if request.method == "POST":
        form = LeaveBalanceForm(request.POST, instance=leave_balance)
        if form.is_valid():
            form.save()
            return redirect('hrhub:employee_leave_balances', slug=leave_balance.employee.slug)  # إعادة التوجيه إلى صفحة التفاصيل
    else:
        form = LeaveBalanceForm(instance=leave_balance)

    return render(request, 'hrhub/leave/leavebalance/update_leave_balance.html', {'form': form, 'leave_balance': leave_balance})


@login_required
@permission_required('hrhub.can_delete_leave_balance', raise_exception=True)
def delete_leave_balance(request, slug):
   
    # جلب سجل الرصيد باستخدام الـ slug
    leave_balance = get_object_or_404(LeaveBalance, slug=slug)

    # حذف السجل
    leave_balance.delete()

    # عرض رسالة نجاح
    messages.success(request, "تم حذف رصيد الإجازة بنجاح.")
    
    # إعادة التوجيه إلى الصفحة الرئيسية أو أي صفحة أخرى
    return redirect('hrhub:employee_leave_balances',  slug=leave_balance.employee.slug)  # قم بتعديل الرابط بما يتناسب مع مشروعك





############ Leave Request  ###############


@login_required
def main_leave_request(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    has_leave_request = request.GET.get('has_leave_request', '')  # إضافة التصفية للإجازات
    leave_type_query = request.GET.get('leave_type', '')
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
    if has_leave_request:
        if has_leave_request.lower() == 'yes':
            query &= Q(basic_info__leave_requests__isnull=False)
        elif has_leave_request.lower() == 'no':
            query &= Q(basic_info__leave_requests__isnull=True)


    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    if leave_type_query:
        query &= Q(basic_info__leave_requests__leave_type__id=leave_type_query)



    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query).distinct()
    leave_types = LeaveType.objects.all()
    

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

    return render(request, 'hrhub/leave/employeeleave/main_leave_request.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'leave_types': leave_types,  # تمرير أنواع الإجازات إلى القالب
    })


@login_required
def employee_leave_requests(request, slug):
    # جلب الموظف باستخدام `slug`
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # جلب جميع طلبات الإجازات المرتبطة بالموظف
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')

    context = {
        'employee': employee,
        'leave_requests': leave_requests
    }
    return render(request, 'hrhub/leave/employeeleave/employee_leave_requests.html', context)



@login_required
def employee_leave_requestsemployee(request, slug):
    # جلب الموظف باستخدام `slug`
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع أنواع الإجازات لعرضها في القائمة المنسدلة
    leave_types = LeaveType.objects.all()

    # استلام نوع الإجازة المحدد من طلب GET
    selected_leave_type = request.GET.get('leave_type', '')

    # تصفية طلبات الإجازات بناءً على النوع المحدد
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')
    if selected_leave_type:
        leave_requests = leave_requests.filter(leave_type_id=selected_leave_type)

    # حساب عدد طلبات الإجازة بعد التصفية
    leave_requests_count = leave_requests.count()

    context = {
        'employee': employee,
        'leave_requests': leave_requests,
        'leave_types': leave_types,
        'selected_leave_type': selected_leave_type,
        'leave_requests_count': leave_requests_count,  # عدد الإجازات لعرضه في القائمة الجانبية
    }
    return render(request, 'hrhub/leave/employeeleave/employee_leave_requestsemployee.html', context)


from django.contrib import messages  # لإضافة رسائل إشعار

from django.contrib import messages  # لإضافة رسائل إشعار


import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.timezone import now

# إعداد الـ logging
logger = logging.getLogger(__name__)

from django.core.exceptions import ValidationError
from django.contrib import messages



@login_required
@permission_required('hrhub.can_add_leave_request', raise_exception=True)
def create_leave_request(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            try:
                leave_request = form.save(commit=False)
                leave_request.employee = employee
                leave_request.created_by = request.user
                leave_request.save()  # قد يرفع ValidationError هنا
                messages.success(request, "تمت إضافة طلب الإجازة بنجاح!")
                return redirect('hrhub:main_leave_request')
            except ValidationError as e:
                # التعامل مع الخطأ وعرض الرسالة للمستخدم
                messages.error(request, e.message)
    else:
        form = LeaveRequestForm()

    return render(request, 'hrhub/leave/employeeleave/add_leave_request.html', {'form': form, 'employee': employee})

@login_required
def leave_request_detail(request, slug):
    # جلب طلب الإجازة بناءً على الـ slug
    leave_request = get_object_or_404(LeaveRequest, slug=slug)
    return render(request, 'hrhub/leave/employeeleave/leave_request_detail.html', {'leave_request': leave_request})



@login_required
@permission_required('hrhub.can_update_leave_request', raise_exception=True)
def update_leave_request(request, slug):
    leave_request = get_object_or_404(LeaveRequest, slug=slug)

    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()  # يتم هنا استدعاء الحفظ مع تحديث البيانات
            return redirect('hrhub:leave_request_detail', slug=leave_request.slug)
    else:
        form = LeaveRequestForm(instance=leave_request)

    return render(request, 'hrhub/leave/employeeleave/update_leave_request.html', {'form': form})


@login_required
@permission_required('hrhub.can_delete_leave_request', raise_exception=True)
def delete_leave_request(request, slug):
   
    # جلب سجل الإجازة باستخدام الـ slug
    leave_request = get_object_or_404(LeaveRequest, slug=slug)
    
    # حذف السجل
    leave_request.delete()
    
    # إرسال رسالة نجاح
    messages.success(request, "تم حذف طلب الإجازة بنجاح.")
    return redirect('hrhub:employee_leave_requests', slug=leave_request.employee.slug)

from decimal import Decimal


import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode

from hrhub.forms.leave_forms import LeaveBalanceCSVUploadForm

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
@permission_required('hrhub.can_add_leave_balance', raise_exception=True)
def upload_leave_balance_csv(request):
    if request.method == 'POST':
        form = LeaveBalanceCSVUploadForm(request.POST, request.FILES)
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
                        leave_type_name = row.get('نوع الإجازة', '').strip()
                        old_balance = row.get('الرصيد القديم', '').strip() or '0'
                        current_balance = row.get('الرصيد الحالي', '').strip() or '0'
                        start_date_str = row.get('تاريخ بدء الرصيد', '').strip()

                        # ✅ تحويل البيانات الرقمية إلى Decimal
                        old_balance = Decimal(old_balance)
                        current_balance = Decimal(current_balance)

                        # ✅ تحويل التاريخ إلى تنسيق صحيح
                        start_date = parse_date(start_date_str) if start_date_str else None

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not leave_type_name:
                            messages.error(request, f"بيانات مفقودة في السطر: {row}.")
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

                        # ✅ البحث عن نوع الإجازة أو إنشاؤه
                        leave_type, _ = LeaveType.objects.get_or_create(
                            name=leave_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ إنشاء slug فريد
                        slug_base = f"{leave_type.name} - {emp_id}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while LeaveBalance.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء أو تحديث سجل LeaveBalance
                        LeaveBalance.objects.update_or_create(
                            employee=basic_info,
                            leave_type=leave_type,
                            defaults={
                                'old_balance': old_balance,
                                'balance': current_balance,
                                'start_date': start_date,
                                'created_by': request.user,
                                'slug': unique_slug
                            }
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات رصيد الإجازات بنجاح!")
                return redirect('hrhub:main_leave_balance')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = LeaveBalanceCSVUploadForm()


    return render(request, 'hrhub/leave/leavebalance/upload_leave_balance_csv.html', {'form': form})









import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from decimal import Decimal

from hrhub.forms.leave_forms import LeaveRequestCSVUploadForm

def parse_date(date_string):
    if not date_string:  # التحقق من أن التاريخ ليس فارغًا
        return None
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None

@login_required
@permission_required('hrhub.can_add_leave_request', raise_exception=True)
def upload_leave_requests_csv(request):
    if request.method == 'POST':
        form = LeaveRequestCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # ✅ قراءة الملف وتحويله إلى قائمة
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # ✅ إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                # ✅ التأكد من أن جميع الأعمدة الأساسية موجودة
                required_fields = ['الرقم الوظيفي', 'نوع الإجازة', 'تاريخ بداية الإجازة', 'تاريخ نهاية الإجازة']
                missing_fields = [field for field in required_fields if field not in reader.fieldnames]

                if missing_fields:
                    messages.error(request, f"❌ الملف يفتقد إلى الأعمدة التالية: {', '.join(missing_fields)}")
                    return redirect('hrhub:upload_leave_requests_csv')

                for row in reader:
                    try:
                        # ✅ قراءة البيانات وتحويل القيم
                        emp_id = row.get('الرقم الوظيفي', '').strip()
                        leave_type_name = row.get('نوع الإجازة', '').strip()
                        start_date_str = row.get('تاريخ بداية الإجازة', '').strip()
                        end_date_str = row.get('تاريخ نهاية الإجازة', '').strip()
                        duration_years = row.get('مدة الإجازة بالسنوات', '').strip() or 0
                        duration_months = row.get('مدة الإجازة بالشهور', '').strip() or 0
                        duration_days = row.get('مدة الإجازة بالأيام', '').strip() or 0
                        total_duration_days = row.get('المدة الاجمالية الإجازة بالأيام', '').strip() or 0
                        status = row.get('حالة الإجازة', '').strip().capitalize()

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        start_date = parse_date(start_date_str)
                        end_date = parse_date(end_date_str)

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not leave_type_name or not start_date or not end_date:
                            messages.error(request, f"❌ بيانات مفقودة أو تنسيق تاريخ غير صحيح في السطر: {row}.")
                            continue

                        # ✅ البحث عن الموظف
                        employee = Employee.objects.filter(username=emp_id).first()
                        if not employee:
                            messages.error(request, f"❌ الموظف برقم {emp_id} غير موجود في النظام.")
                            continue

                        # ✅ البحث عن BasicInfo للموظف
                        basic_info = BasicInfo.objects.filter(emp_id=employee).first()
                        if not basic_info:
                            messages.error(request, f"❌ لم يتم العثور على بيانات الموظف الأساسية للرقم الوظيفي {emp_id}.")
                            continue

                        # ✅ البحث عن نوع الإجازة أو إنشاؤه
                        leave_type, _ = LeaveType.objects.get_or_create(
                            name=leave_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ حساب مدة الإجازة بالأيام
                        if start_date and end_date:
                            total_days = (end_date - start_date).days + 1
                        else:
                            total_days = int(total_duration_days) if total_duration_days else 0

                        # ✅ التحقق من حالة الإجازة
                        if status not in ['Pending', 'Approved', 'Rejected']:
                            status = 'Pending'

                        # ✅ إنشاء سجل LeaveRequest
                        leave_request = LeaveRequest.objects.create(
                            employee=basic_info,
                            leave_type=leave_type,
                            start_date=start_date,
                            end_date=end_date,
                            duration_years=int(duration_years),
                            duration_months=int(duration_months),
                            duration_days=int(duration_days),
                            total_duration_days=total_days,
                            status=status
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات الإجازات بنجاح!")
                return redirect('hrhub:main_leave_request')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = LeaveRequestCSVUploadForm()

    return render(request, 'hrhub/leave/employeeleave/upload_leave_requests_csv.html', {'form': form})



import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def download_leave_balance_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="leave_balance_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الرقم الوظيفي', 'نوع الإجازة', 'الرصيد القديم', 'الرصيد الحالي', 'تاريخ بدء الرصيد']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        ['7901021970', 'اجازة عادية', '10.0', '15.0', '01/01/2024']
    ]
    writer.writerows(example_rows)

    return response




import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def download_leave_requests_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="leave_requests_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الرقم الوظيفي', 'نوع الإجازة', 'تاريخ بداية الإجازة', 'تاريخ نهاية الإجازة', 'مدة الإجازة بالسنوات', 'مدة الإجازة بالشهور', 'مدة الإجازة بالأيام', 'المدة الاجمالية الإجازة بالأيام', 'حالة الإجازة']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        ['7801201970', 'إجازة سنوية', '10/02/2024', '20/02/2024', '0', '0', '10', '10', 'Pending'],
        ['7801201971', 'إجازة مرضية', '15/03/2024', '18/03/2024', '0', '0', '3', '3', 'Approved']
    ]
    writer.writerows(example_rows)

    return response