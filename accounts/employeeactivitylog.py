from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.encoding import smart_str
import csv
from .models import Employee, EmployeeActivityLog
from hrhub.models.office_position_models import Office

from django.db.models import Q

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from hrhub.models.office_position_models import Office

def employee_activity_view(request):
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

    return render(request, 'accounts/accountsaffairs/employee_activity.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
    })



def export_to_csv(request, employees):
    # تجهيز البيانات للتصدير
    employee_data = []
    for employee in employees:
        full_name = employee.basic_info.get_full_name() if hasattr(employee, 'basic_info') else 'لا يوجد اسم كامل'
        latest_login = employee.latest_login if hasattr(employee, 'latest_login') else 'لم يقم بتسجيل الدخول بعد'
        is_logged_in = 'مسجل الدخول' if getattr(employee, 'is_logged_in', False) else 'غير مسجل الدخول'
        
        employee_data.append({
            'username': employee.username,
            'full_name': full_name,
            'is_active': employee.is_active,
            'created_at': employee.created_at,
            'updated_at': employee.updated_at,
            'latest_login': latest_login,
            'is_logged_in': is_logged_in
        })

    # إنشاء ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="employee_activity.csv"'
    
    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM (Byte Order Mark) لملف CSV

    writer = csv.DictWriter(response, fieldnames=employee_data[0].keys())

    # كتابة الرأس باستخدام smart_str للتأكد من أن النصوص بالعربية ستظهر بشكل صحيح
    writer.writeheader()

    # كتابة البيانات
    for data in employee_data:
        writer.writerow({
            'username': smart_str(data['username'], encoding='utf-8', errors='ignore'),
            'full_name': smart_str(data['full_name'], encoding='utf-8', errors='ignore'),
            'is_active': smart_str(data['is_active'], encoding='utf-8', errors='ignore'),
            'created_at': smart_str(data['created_at'], encoding='utf-8', errors='ignore'),
            'updated_at': smart_str(data['updated_at'], encoding='utf-8', errors='ignore'),
            'latest_login': smart_str(data['latest_login'], encoding='utf-8', errors='ignore'),
            'is_logged_in': smart_str(data['is_logged_in'], encoding='utf-8', errors='ignore')
        })

    return response



from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from .models import Employee
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from .models import Employee

from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from .models import Employee
import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.utils.encoding import smart_str  # استيراد smart_str من Django
from .models import Employee
import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from .models import Employee

def employee_activity(request, slug):
    # الحصول على الموظف باستخدام الـ slug
    employee = get_object_or_404(Employee, slug=slug)
    
    # الحصول على جميع الأنشطة الخاصة بالموظف
    activity_logs = employee.activity_logs.all()

    # التحقق مما إذا كانت هناك تواريخ للتصفية
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # التصفية بناءً على التاريخ إذا تم إدخال التواريخ
    if start_date:
        start_date = parse_date(start_date)
        activity_logs = activity_logs.filter(timestamp__gte=start_date)
    
    if end_date:
        end_date = parse_date(end_date)
        activity_logs = activity_logs.filter(timestamp__lte=end_date)

    action_search = request.GET.get('action_search')
    if action_search:
        activity_logs = activity_logs.filter(action=action_search)
    
    
    activity_logs_accounts = activity_logs.count()
    
    # التحقق من التصدير إلى CSV
    if request.GET.get('export_csv') == 'true':
        return export_activity_logs_to_csv(activity_logs)

    # عرض الأنشطة مع التواريخ المحددة والأنشطة غير المقيدة
    return render(request, 'accounts/accountsaffairs/employee_all_activity.html', {
        'employee': employee,
        'activity_logs': activity_logs,
        'activity_logs_accounts': activity_logs_accounts,
    })



def export_activity_logs_to_csv(activity_logs):
    # إعداد استجابة HTTP لتحميل الملف
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employee_activity_logs.csv"'
    
    # تحديد الترميز utf-8-sig لضمان التوافق مع Excel والتطبيقات الأخرى
    response.charset = 'utf-8-sig'

    # إنشاء كاتب CSV
    writer = csv.writer(response)
    
    # كتابة رؤوس الأعمدة مباشرة باستخدام ترميز UTF-8
    writer.writerow(['الحدث', 'التاريخ', 'عنوان الـ IP', 'المتصفح', 'نظام التشغيل', 'الجهاز'])
    
    # كتابة البيانات
    for log in activity_logs:
        writer.writerow([log.action, log.timestamp, log.ip_address,
                         log.browser, log.operating_system, log.device])
    
    return response
