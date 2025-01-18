from urllib import request
from django.shortcuts import render, redirect, get_object_or_404  # استيراد الدوال المستخدمة في معالجة الطلبات والردود.
from django.contrib.auth.decorators import login_required , user_passes_test  # استيراد الديكوريتور للتحقق من أن المستخدم مسجل الدخول.
from django.http import HttpResponseForbidden, HttpResponse  # استيراد ردود HTTP للاستخدام في التحكم في الوصول والاستجابة.
from django.core.paginator import Paginator  # استيراد الكائن Paginator لتقسيم البيانات إلى صفحات.
from django.utils.dateparse import parse_date  # استيراد دالة parse_date لتحويل سلسلة نصية إلى كائن تاريخ.
# from .models import Employee, LoginActivity  # استيراد النماذج المستخدمة (Employee وLoginActivity) من الوحدة المحلية.
import csv  # استيراد مكتبة CSV للتعامل مع ملفات CSV.
import logging  # استيراد مكتبة logging لتسجيل الرسائل والأخطاء.
from django.db.models import Q
from django.contrib import messages
from django.utils.encoding import smart_str

from django.db.models import Q

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from hrhub.models.office_position_models import Office

logger = logging.getLogger(__name__)  # إنشاء كائن logger لتسجيل الرسائل مع اسم الوحدة الحالية.



from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render


def accounts_main_affiars(request):
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

    return render(request, 'accounts/accountsaffairs/accounts_main_affiars.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
    })



@login_required  # هذا الديكور يتأكد من أن المستخدم مسجل الدخول قبل الوصول إلى هذه الصفحة
def accounts_main_page(request):
    # تحقق مما إذا كان المستخدم ليس مديراً عاماً (Superuser)
    if not request.user.is_superuser:
        # في حال عدم كونه مديراً عاماً، أضف رسالة خطأ توضح أنه لا يملك الصلاحيات للوصول إلى هذه الصفحة
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        
        # إعادة توجيه المستخدم إلى صفحة عرض الملف الشخصي
        return redirect('accounts:view_profile')  

    # في حال كان المستخدم مديراً عاماً، قم بعرض الصفحة الرئيسية لإدارة الحسابات
    return render(request, 'accounts/accountsaffairs/accounts_main_page.html')

import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.db.models import Q

############################ 




@login_required
def toggle_employee_status(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.is_active = not employee.is_active  # عكس حالة is_active
    employee.save()
    if employee.is_active:
        message = f"تم تفعيل حساب {employee.username} بنجاح."
    else:
        message = f"تم تعطيل حساب {employee.username} بنجاح."
    # إرسال رسالة تأكيد (اختياري)
    messages.success(request, message)
    return redirect('accounts:accounts_main_affiars')  # إعادة التوجيه إلى قائمة الموظفين أو أي 



def employee_list(request):
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

    return render(request, 'accounts/accountsaffairs/employee_list.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
    })




import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from .models import Employee

@login_required
def export_filtered_employee_csv(request):
    # جلب القيم من استعلام البحث
    username_query = request.GET.get('username', '')  # اسم المستخدم
    firstname_query = request.GET.get('firstname', '')  # الاسم الأول
    secondname_query = request.GET.get('secondname', '')  # الاسم الثاني
    thirdname_query = request.GET.get('thirdname', '')  # الاسم الثالث
    results_per_page = request.GET.get('results_per_page', '10')  # عدد النتائج لكل صفحة (افتراضي 10)

    # التأكد من صحة القيمة المعطاة لـ results_per_page
    try:
        results_per_page = int(results_per_page)
    except ValueError:
        results_per_page = 10  # القيمة الافتراضية إذا كانت المدخلة غير صحيحة

    # جلب جميع الموظفين
    employees = Employee.objects.all()

    # تطبيق الفلاتر بناءً على المدخلات
    if username_query:
        employees = employees.filter(username__icontains=username_query)
    if firstname_query:
        employees = employees.filter(basic_info__firstname__icontains=firstname_query)
    if secondname_query:
        employees = employees.filter(basic_info__secondname__icontains=secondname_query)
    if thirdname_query:
        employees = employees.filter(basic_info__thirdname__icontains=thirdname_query)

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="filtered_employees.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM (Byte Order Mark) لملف CSV

    writer = csv.writer(response)

    # كتابة الرأس (العناوين)
    writer.writerow([
        smart_str('اسم المستخدم', encoding='utf-8', errors='ignore'),
        smart_str('الاسم الأول', encoding='utf-8', errors='ignore'),
        smart_str('الاسم الثاني', encoding='utf-8', errors='ignore'),
        smart_str('الاسم الثالث', encoding='utf-8', errors='ignore'),
        smart_str('تفعيل الحساب', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('معلومات أساسية', encoding='utf-8', errors='ignore'),
    ])

    # كتابة البيانات بعد تطبيق الفلاتر
    for employee in employees:
        # التحقق إذا كان الموظف لديه معلومات أساسية
        basic_info = getattr(employee, 'basic_info', None)
        if basic_info:
            firstname = basic_info.firstname
            secondname = basic_info.secondname
            thirdname = basic_info.thirdname
            has_basic_info = "نعم"
        else:
            firstname = 'ليس لديهم معلومات'
            secondname = 'ليس لديهم معلومات'
            thirdname = 'ليس لديهم معلومات'
            has_basic_info = "لا"

        created_at = employee.created_at.strftime('%Y-%m-%d %H:%M:%S') if employee.created_at else 'غير معروف'
        
        writer.writerow([
            smart_str(employee.username, encoding='utf-8', errors='ignore'),
            smart_str(firstname, encoding='utf-8', errors='ignore'),
            smart_str(secondname, encoding='utf-8', errors='ignore'),
            smart_str(thirdname, encoding='utf-8', errors='ignore'),
            'نعم' if employee.is_active else 'لا',
            smart_str(created_at, encoding='utf-8', errors='ignore'),
            smart_str(has_basic_info, encoding='utf-8', errors='ignore')
        ])

    return response




def change_employee_password(request, employee_id):
    # البحث عن الموظف باستخدام id
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == "POST":
        new_password = request.POST.get('new_password')
        
        # تغيير كلمة المرور
        employee.set_password(new_password)
        employee.save()
        
        # إرسال رسالة تأكيد
        messages.success(request, "تم تغيير كلمة المرور بنجاح.")
        
        return redirect('accounts:accounts_main_affiars')  # إعادة التوجيه إلى صفحة تفاصيل الموظف

    return render(request, 'accounts/accountsaffairs/emplpoyee_change_password.html', {'employee': employee})






    
@login_required
def employee_login_activity(request, username):
    if not request.user.is_superuser:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        return redirect('accounts:view_profile') 
    employee = get_object_or_404(Employee, username=username)

    

    # Get the date range from GET parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Filter login activities based on the date range
    login_activities = employee.login_activities.all()
    if start_date and end_date:
        login_activities = login_activities.filter(timestamp__range=[start_date, end_date])


    total_count = login_activities.count()

    # Check if CSV export is requested and the filtered queryset is passed
    if request.GET.get('export') == 'csv':
        # Ensure that the filtered login activities are exported
        filtered_activities = login_activities
        return export_to_csv(filtered_activities)

    # Pagination
    page_size = request.GET.get('page_size', '10')
    try:
        page_size = int(page_size)
        if page_size <= 0:
            page_size = 10
    except ValueError:
        page_size = 10

    paginator = Paginator(login_activities, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'page_size': page_size,
        'total_count': total_count,
    }
    return render(request, 'accounts/accountsaffairs/employee_login_activity.html', context)



def export_to_csv(activities):
    """
    Generate a CSV response for the given login activities.
    
    Args:
        activities: QuerySet of LoginActivity objects to be exported to CSV.
    
    Returns:
        HttpResponse: A CSV file attachment containing the login activities.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="login_activities.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Employee', 'Timestamp', 'IP Address', 'User Agent', 'OS Info'])
    
    for activity in activities:
        writer.writerow([
            f"{activity.employee.get_full_name()} ({activity.employee.username})",
            activity.timestamp,
            activity.ip_address,
            activity.user_agent,
            activity.os_info, 
        ])
    
    return response


from django.db.models import Q

# @login_required
# def login_activity_list(request):
#     if not request.user.is_superuser:
#         messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
#         return redirect('accounts:view_profile') 
    
#     # الحصول على نطاق التاريخ من المعلمات GET
#     start_date_str = request.GET.get('start_date')
#     end_date_str = request.GET.get('end_date')
#     start_date = parse_date(start_date_str) if start_date_str else None
#     end_date = parse_date(end_date_str) if end_date_str else None

#     # الحصول على الرقم الوظيفي من المعلمات GET
#     employee_id = request.GET.get('employee_id')

#     # جلب جميع الأنشطة وترتيبها حسب التاريخ
#     activities = LoginActivity.objects.all().order_by('-timestamp')

#     # تطبيق الفلترة حسب نطاق التاريخ إن وُجد
#     if start_date and end_date:
#         activities = activities.filter(timestamp__range=[start_date, end_date])

#     # تطبيق الفلترة حسب الرقم الوظيفي إن وُجد
#     if employee_id:
#         activities = activities.filter(employee__username__icontains=employee_id)

#     total_count = activities.count()

#     # تصدير إلى CSV إذا طلب ذلك
#     if request.GET.get('export') == 'csv':
#         return login_activity_list_export_to_csv(activities)

#     # Pagination
#     page_size = request.GET.get('page_size', '10')
#     try:
#         page_size = int(page_size)
#         if page_size <= 0:
#             page_size = 10
#     except ValueError:
#         page_size = 10

#     paginator = Paginator(activities, page_size)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # تمرير السجلات والفلاتر إلى القالب
#     context = {
#         'activities': page_obj,
#         'start_date': start_date_str,
#         'end_date': end_date_str,
#         'employee_id': employee_id,
#         'page_size': page_size,
#         'total_count': total_count,
#     }
#     return render(request, 'accounts/accountsaffairs/login_activity_list.html', context)

# def login_activity_list_export_to_csv(activities):
#     # إعداد رد CSV
#     response = HttpResponse(content_type='text/csv; charset=utf-8')
#     response['Content-Disposition'] = 'attachment; filename="login_activities.csv"'
#     response.write('\ufeff'.encode('utf8'))  # إضافة BOM لتوافق Excel

#     writer = csv.writer(response)
#     # كتابة العناوين بالعربية والإنجليزية
#     writer.writerow([
#         smart_str('الموظف (Employee)', encoding='utf-8', errors='ignore'),
#         smart_str('تاريخ ووقت الدخول (Timestamp)', encoding='utf-8', errors='ignore'),
#         smart_str('المتصفح (Browser)', encoding='utf-8', errors='ignore'),
#         smart_str('نظام التشغيل (OS)', encoding='utf-8', errors='ignore'),
#     ])

#     # كتابة البيانات
#     for activity in activities:
#         writer.writerow([
#             smart_str(activity.employee.username, encoding='utf-8', errors='ignore'),
#             smart_str(activity.timestamp, encoding='utf-8', errors='ignore'),
#             smart_str(activity.user_agent, encoding='utf-8', errors='ignore'),
#             smart_str(activity.os_info, encoding='utf-8', errors='ignore'),
#         ])

#     return response


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee
from .forms import EmployeeApprovalForm


@login_required
def approve_employee(request, slug):
    employee = get_object_or_404(Employee, slug=slug)  # البحث عن الموظف باستخدام الـ slug

    if request.method == 'POST':
        form = EmployeeApprovalForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('accounts:employee_list')  # أو أي صفحة أخرى ترغب في إعادة التوجيه إليها
    else:
        form = EmployeeApprovalForm(instance=employee)

    return render(request, 'accounts/accountsaffairs/approve_employee.html', {'form': form, 'employee': employee})




from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.encoding import smart_str
import csv
from .models import Employee, EmployeeActivityLog

def employee_employee_view(request):
    employees = Employee.objects.all()
    
    return render(request, 'accounts/accountsaffairs/employee_employee_view.html', 
       {'employees': employees})



def change_employee_password(request, employee_id):
    # البحث عن الموظف باستخدام id
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == "POST":
        new_password = request.POST.get('new_password')
        
        # تغيير كلمة المرور
        employee.set_password(new_password)
        employee.save()
        
        # إرسال رسالة تأكيد
        messages.success(request, "تم تغيير كلمة المرور بنجاح.")
        
        return redirect('accounts:employee_employee_view')  # إعادة التوجيه إلى صفحة تفاصيل الموظف

    return render(request, 'accounts/accountsaffairs/emplpoyee_change_password.html', {'employee': employee})




