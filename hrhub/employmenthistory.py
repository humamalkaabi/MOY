from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from hrhub.forms.Employment_Forms import EmploymentHistoryForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden

from personalinfo.models import BasicInfo
from django.shortcuts import render
from hrhub.models.employement_models import EmploymentHistory, EmployementType
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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date
from hrhub.models.hr_utilities_models import PlaceOfEmployment
from accounts.models import Employee
from django.db.models import Exists, OuterRef

from django.db.models import Exists, OuterRef
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied





@login_required
def employee_employment_history(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    has_job = request.GET.get('has_job', '')
    is_employment_counted = request.GET.get('is_employment_counted', '')
    employment_type_id = request.GET.get('employment_type', '')
    results_per_page = request.GET.get('results_per_page', '10')

    # التأكد من صحة النتائج لكل صفحة
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    # بناء الاستعلام
    query = Q()

    if username_query:
        query &= Q(username__icontains=username_query)
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )
    if has_job:
        if has_job.lower() == 'yes':
            query &= Q(basic_info__employment_histories__isnull=False)
        elif has_job.lower() == 'no':
            query &= Q(basic_info__employment_histories__isnull=True)

    if gender_query:
        query &= Q(basic_info__gender=gender_query)

    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    if is_employment_counted:
        if is_employment_counted.lower() == 'false':
            query &= Q(basic_info__employment_histories__employee_type__is_employment_type_counted=False)
        elif is_employment_counted.lower() == 'true':
            query &= Q(basic_info__employment_histories__employee_type__is_employment_type_counted=True)

    if employment_type_id:
        query &= Q(basic_info__employment_histories__employee_type__id=employment_type_id)

    # إضافة الحقل الديناميكي "has_service"
    employees = Employee.objects.filter(query).annotate(
        has_service=Exists(
            EmploymentHistory.objects.filter(basic_info=OuterRef('basic_info'))
        )
    )

    employment_types = EmployementType.objects.all()

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(employees, results_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # عد النتائج
    employee_count = employees.count()

    return render(request, 'hrhub/employee_employment_history/employee_employment_history.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'employment_types': employment_types,
    })


from django.db.models import Count, Min


@login_required
def employment_statistics(request):
    # احصائيات أنواع التوظيف
    most_common_employment_type = EmployementType.objects.annotate(
        num_employees=Count('employment_histories')
    ).order_by('-num_employees').first()  # الحصول على أكثر نوع توظيف عدد الموظفين فيه
    
    # أقدم تاريخ بداية توظيف
    earliest_start_date = EmploymentHistory.objects.aggregate(
        earliest_start_date=Min('start_date')
    )['earliest_start_date']
    
    # أكثر موظف لديه أنواع توظيف متعددة
    employees_with_multiple_employment_types = EmploymentHistory.objects.values('employee').annotate(
        num_employment_types=Count('employee_type', distinct=True)
    ).filter(num_employment_types__gt=1).order_by('-num_employment_types')

    # الحصول على معلومات الموظفين من EmploymentHistory
    employees_info = BasicInfo.objects.filter(id__in=[e['employee'] for e in employees_with_multiple_employment_types])

    context = {
        'most_common_employment_type': most_common_employment_type,
        'earliest_start_date': earliest_start_date,
        'employees_with_multiple_employment_types': zip(employees_info, employees_with_multiple_employment_types),
    }
    

    return render(request, 'hrhub/employee_employment_history/employment_statistics.html', context)



@login_required
def employment_history_detail(request, slug):
    # الحصول على الموظف باستخدام الـ slug
    employee = get_object_or_404(BasicInfo, slug=slug)
    # جلب السجلات الوظيفية المرتبطة بالموظف
    employment_histories = EmploymentHistory.objects.filter(basic_info=employee)
    
    context = {
        'employee': employee,
        'employment_histories': employment_histories,
    }
    return render(request, 'hrhub/employee_employment_history/employment_history_detail.html', context)



@login_required
def employment_history_detailemployee(request, slug):
    # الحصول على الموظف باستخدام الـ slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع أنواع الوظائف لعرضها في القائمة المنسدلة
    employment_types = EmployementType.objects.all()

    # استلام نوع الوظيفة المحدد من طلب GET
    selected_employment_type = request.GET.get('employee_type', '')

    # تصفية السجلات الوظيفية بناءً على النوع المحدد
    employment_histories = EmploymentHistory.objects.filter(basic_info=employee)
    if selected_employment_type:
        employment_histories = employment_histories.filter(employee_type_id=selected_employment_type)

    # حساب عدد السجلات بعد التصفية
    employment_histories_count = employment_histories.count()

    context = {
        'employee': employee,
        'employment_histories': employment_histories,
        'employment_types': employment_types,
        'selected_employment_type': selected_employment_type,
        'employment_histories_count': employment_histories_count,  # عدد السجلات لعرضه في القائمة الجانبية
    }
    return render(request, 'hrhub/employee_employment_history/employment_history_detailemployee.html', context)




@login_required
def employment_single_history_detail(request, slug):
    # الحصول على السجل الوظيفي باستخدام slug
    employment_history = get_object_or_404(EmploymentHistory, slug=slug)

    context = {
        'employment_history': employment_history,
    }
    return render(request, 'hrhub/employee_employment_history/employment_single_history_detail.html', context)

@login_required
@permission_required('hrhub.can_add_employment_history', raise_exception=True)
def add_employment_history(request, slug):
    # الحصول على الموظف بناءً على الـ slug
    employee = BasicInfo.objects.get(slug=slug)

    if request.method == 'POST':
        form = EmploymentHistoryForm(request.POST, request.FILES)
        if form.is_valid():
            # تعيين الموظف في النموذج بعد التحقق من صحة البيانات
            employment_history = form.save(commit=False)
            employment_history.basic_info = employee
            employment_history.save()

            return redirect('hrhub:employee_employment_history')
    else:
        form = EmploymentHistoryForm()

    return render(request, 'hrhub/employee_employment_history/add_employment_history.html', {
        'form': form, 'employee': employee
    })





# في ملف views.py
@login_required
@permission_required('hrhub.can_update_employment_history', raise_exception=True)
def employment_history_update(request, slug):
    employment_history = get_object_or_404(EmploymentHistory, slug=slug)

    if request.method == 'POST':
        form = EmploymentHistoryForm(request.POST, request.FILES, instance=employment_history)
        if form.is_valid():
            form.save()
            return redirect('hrhub:employment_single_history_detail', slug=employment_history.slug)
    else:
        form = EmploymentHistoryForm(instance=employment_history)

    return render(request, 'hrhub/employee_employment_history/employment_history_update.html', {'form': form, 'employment_history': employment_history})





@login_required
@permission_required('hrhub.can_delete_employment_history', raise_exception=True)
def delete_employment_history_update(request, slug):
   
    
    employment_history = get_object_or_404(EmploymentHistory, slug=slug)
    
    employment_history.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('hrhub:employee_employment_history')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك





import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from hrhub.forms.employee_history_forms import EmploymentHistoryCSVUploadForm

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
@permission_required('hrhub.can_add_employment_history', raise_exception=True)
def upload_employment_history_csv(request):
    if request.method == 'POST':
        form = EmploymentHistoryCSVUploadForm(request.POST, request.FILES)
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
                        employment_type_name = row.get('نوع التوظيف', '').strip()
                        start_date_str = row.get('تاريخ البدء', '').strip()
                        end_date_str = row.get('تاريخ الانتهاء', '').strip()
                        duration_days = row.get('مدة الخدمة - بالأيام', '').strip() or None
                        duration_months = row.get('مدة الخدمة - بالأشهر', '').strip() or None
                        duration_years = row.get('مدة الخدمة - بالسنوات', '').strip() or None
                        employment_place_name = row.get('مكان العمل', '').strip()
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        start_date = parse_date(start_date_str) if start_date_str else None
                        end_date = parse_date(end_date_str) if end_date_str else None

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not employment_type_name or not start_date:
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

                        # ✅ البحث عن نوع التوظيف أو إنشاؤه
                        employment_type, _ = EmployementType.objects.get_or_create(
                            name=employment_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ البحث عن مكان العمل أو إنشاؤه (تصحيح البحث باستخدام name_in_arabic)
                        employment_place, _ = PlaceOfEmployment.objects.get_or_create(
                            name_in_arabic=employment_place_name
                        )

                        # ✅ إنشاء slug فريد
                        slug_base = f"{employment_type.name} - {emp_id}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while EmploymentHistory.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء سجل EmploymentHistory
                        employment_history = EmploymentHistory.objects.create(
                            created_by=request.user,
                            basic_info=basic_info,
                            employee_type=employment_type,
                            employee_place=employment_place,
                            start_date=start_date,
                            end_date=end_date,
                            employee_duration_year=int(duration_years) if duration_years else None,
                            employee_duration_month=int(duration_months) if duration_months else None,
                            employee_duration_day=int(duration_days) if duration_days else None,
                            comments=comments,
                            slug=unique_slug
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات التوظيف بنجاح!")
                return redirect('hrhub:employee_employment_history')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = EmploymentHistoryCSVUploadForm()

    return render(request, 'hrhub/employee_employment_history/upload_employment_history_csv.html', {'form': form})
