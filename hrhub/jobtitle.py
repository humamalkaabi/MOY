from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from accounts.models import Employee
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify
from locations.models  import Governorate
import csv
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.utils.translation import gettext as _
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models.employee_job_title_models import JobTitle, EmployeeJobTitle
from hrhub.forms.JobForm import JobTitleForm

from personalinfo.models import BasicInfo

# views.py
from django.shortcuts import render, redirect
from hrhub.models.employee_job_title_models import EmployeeJobTitleSettings
from hrhub.forms.JobForm import EmployeeJobTitleSettingsForm, EmployeeJobTitleCSVUploadForm
from django.contrib import messages

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Prefetch

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
def main_job_title(request):
    # استعلام عن العناوين الوظيفية الرئيسية فقط (التي ليس لها أب)
    jobtitles = JobTitle.objects.filter(parent__isnull=True)

    context = {
        'jobtitles': jobtitles,
        'parents': jobtitles,
        'jobtitles_count': jobtitles.count(),   # للحصول على قائمة بالعناوين الرئيسية فقط
    }

    return render(request, 'hrhub/jobtitle/main_job_title.html', context)

def sub_job_titles(request, parent_slug):
    # الحصول على العنوان الوظيفي الأب بناءً على الـ slug
    parent = get_object_or_404(JobTitle, slug=parent_slug)

    # جلب جميع الأبناء (المباشرين وغير المباشرين)
    all_descendants = parent.get_descendants()

    context = {
        'parent': parent,
        'sub_titles': all_descendants,  # جميع الأبناء
    }

    return render(request, 'hrhub/jobtitle/sub_job_titles.html', context)



@login_required
@permission_required('hrhub.can_update_job_title', raise_exception=True)
def update_job_title(request, slug):
    # الحصول على السجل المطلوب تعديله باستخدام slug
    job_title = get_object_or_404(JobTitle, slug=slug)

    if request.method == 'POST':
        # تحديث البيانات باستخدام النموذج
        form = JobTitleForm(request.POST, instance=job_title)
        if form.is_valid():
            new_parent = form.cleaned_data.get('parent')

            # التحقق من أن العقدة الأب الجديدة ليست أحد الأحفاد
            if new_parent and new_parent in job_title.get_descendants():
                form.add_error('parent', "لا يمكن تعيين العنوان الوظيفي كأحد أحفاده.")
            else:
                job_title = form.save(commit=False)
                job_title.created_by = request.user  # تحديث المستخدم الذي قام بالتعديل
                job_title.save()
                messages.success(request, "تم تحديث العنوان الوظيفي بنجاح.")
                return redirect('hrhub:main_job_title')  # تعديل المسار حسب الحاجة
    else:
        # عرض النموذج مع البيانات الحالية
        form = JobTitleForm(instance=job_title)

    context = {
        'form': form,
        'job_title': job_title
    }
    return render(request, 'hrhub/jobtitle/update_job_title.html', context)





@login_required
@permission_required('hrhub.can_add_job_title', raise_exception=True)
def add_job_title(request):
    if request.method == 'POST':
        form = JobTitleForm(request.POST)
        if form.is_valid():
            job_title = form.save(commit=False)
            job_title.created_by = request.user  # ربط بـ login user
            job_title.is_approved = True
            job_title.save()
            return redirect('hrhub:main_job_title')  # يمكنك تعديل URL حسب الحاجة
    else:
        form = JobTitleForm()
    return render(request, 'hrhub/jobtitle/add_job_title.html', {'form': form})


@login_required
def job_title_detail(request, slug):
    # جلب العنوان الوظيفي المطلوب بناءً على slug
    job_title = get_object_or_404(JobTitle, slug=slug)

    context = {
        'job_title': job_title
    }
    return render(request, 'hrhub/jobtitle/job_title_detail.html', context)





@login_required
@permission_required('hrhub.can_delete_job_title', raise_exception=True)
def delete_job_title(request, slug):
    # التحقق من صلاحيات المستخدم
    if not request.user.has_perm('hrhub.delete_jobtitle'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    # جلب سجل الديانة باستخدام الـ slug
    religion = get_object_or_404(JobTitle, slug=slug)
    
    # حذف السجل
    religion.delete()
    
    messages.success(request, "تم حذف العنوان بنجاح.")
    return redirect('hrhub:main_job_title')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك





# ######################################  Employee job title #######################################



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db.models import Q  # لاستيراد Q لتطبيق عوامل تصفية معقدة
from django.core.paginator import Paginator

@login_required
def main_employee_job_title(request):

    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_job_title = request.GET.get('has_job_title', '')
    job_title_parent = request.GET.get('job_title_parent', '') 
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
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

    if has_job_title:
        if has_job_title.lower() == 'yes':
            query &= Q(basic_info__employee_job_title__isnull=False)
        elif has_job_title.lower() == 'no':
            query &= Q(basic_info__employee_job_title__isnull=True)
    if job_title_parent:
        query &= Q(basic_info__employee_job_title__employee_job_title__parent_id=job_title_parent)


    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)

    
    
   
    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    job_title_parents = JobTitle.objects.filter(parent__isnull=True)
    employees = Employee.objects.filter(query).prefetch_related('basic_info')

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

    return render(request, 'hrhub/jobtitle/employee_job_title/main_employee_job_title.html', {
        'employees': page_obj,
        'employee_count': employee_count,
         'job_title_parents': job_title_parents,
        'results_per_page': results_per_page,
    })

@login_required

def employee_job_title_detail(request, slug):
    """
    عرض تفاصيل العنوان الوظيفي لموظف معين باستخدام `slug`
    """
    employee_job_title = get_object_or_404(EmployeeJobTitle, slug=slug)
    
    return render(request, 'hrhub/jobtitle/employee_job_title/employee_job_title_detail.html', {
        'employee_job_title': employee_job_title
    })

@login_required
def update_employee_job_title_settings(request):
    # الحصول على السجل الوحيد الموجود أو إنشاء واحد جديد
    try:
        settings = EmployeeJobTitleSettings.objects.get(id=1)
    except EmployeeJobTitleSettings.DoesNotExist:
        settings = None
    
    if request.method == 'POST':
        form = EmployeeJobTitleSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الإعدادات بنجاح')
            return redirect('hrhub:main_employee_job_title')
    else:
        form = EmployeeJobTitleSettingsForm(instance=settings)

    return render(request, 'hrhub/jobtitle/employee_job_title/update_employee_job_title_settings.html', {'form': form})


from django.shortcuts import render, get_object_or_404

@login_required
def employee_job_titles(request, slug):
    # استرجاع الموظف باستخدام الـ slug
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    # استرجاع العناوين الوظيفية للموظف بناءً على slug
    employee_job_titles = EmployeeJobTitle.objects.filter(basic_info=basic_info)

    # إرسال البيانات إلى القالب
    return render(request, 'hrhub/jobtitle/employee_job_title/employee_job_titles.html', {'employee_job_titles': employee_job_titles, 'basic_info': basic_info})




@login_required
def employee_job_titlesemployee(request, slug):
    # استرجاع الموظف باستخدام الـ slug
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    # استرجاع العناوين الوظيفية للموظف بناءً على slug
    employee_job_titles = EmployeeJobTitle.objects.filter(basic_info=basic_info)

    # إرسال البيانات إلى القالب
    return render(request, 'hrhub/jobtitle/employee/employee_job_titlesemployee.html', {'employee_job_titles': employee_job_titles, 'basic_info': basic_info})


@login_required
@permission_required('hrhub.can_update_employee_job_title', raise_exception=True)
def update_employee_job_title(request, slug):
    # جلب الكائن EmployeeJobTitle باستخدام slug
    employee_job_title = get_object_or_404(EmployeeJobTitle, slug=slug)

    # إذا كانت البيانات مستلمة عبر POST، يتم معالجتها
    if request.method == 'POST':
        form = EmployeeJobTitleForm(request.POST, instance=employee_job_title)
        if form.is_valid():
            form.save()  # حفظ التحديثات
            return redirect('hrhub:main_employee_job_title')  # تغيير إلى URL مناسب
    else:
        form = EmployeeJobTitleForm(instance=employee_job_title)  # تحميل البيانات لتعديلها

    return render(request, 'hrhub/jobtitle/employee_job_title/update_employee_job_title.html', {'form': form, 'employee_job_title': employee_job_title})



@login_required
@permission_required('hrhub.can_delete_employee_job_title', raise_exception=True)
def delete_employee_job_title(request, slug):
    # التحقق من صلاحيات المستخدم
    
    # جلب سجل العنوان الوظيفي باستخدام الـ slug
    employee_job_title = get_object_or_404(EmployeeJobTitle, slug=slug)
    
    # حذف السجل
    employee_job_title.delete()
    
    # إضافة رسالة نجاح
    messages.success(request, "تم حذف العنوان الوظيفي بنجاح.")
    
    # إعادة التوجيه إلى الصفحة المناسبة
    return redirect('hrhub:main_employee_job_title')  # استبدل `yourapp:employee_job_title_list` بالرابط المناسب لمشروعك


# return redirect('hrhub:main_employee_job_title')  # إعادة التوجيه إلى قائمة العناوين الوظيفية


from .forms.JobForm import EmployeeJobTitleForm

from django.http import JsonResponse

def get_child_job_titles(request, parent_id):
    if request.method == 'GET':
        try:
            children = JobTitle.objects.filter(parent_id=parent_id).values('id', 'title_in_arabic')
            return JsonResponse(list(children), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def get_related_job_titles(request, job_title_id):
    if request.method == 'GET':
        try:
            related_titles = JobTitle.objects.filter(parent_id=job_title_id).values('id', 'title_in_arabic')
            return JsonResponse(list(related_titles), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
@permission_required('hrhub.can_add_employee_job_title', raise_exception=True)
def create_employee_job_title(request, slug):
    # جلب الكائن BasicInfo باستخدام slug
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    # إذا كانت البيانات مستلمة عبر POST، يتم معالجتها
    if request.method == 'POST':
        form = EmployeeJobTitleForm(request.POST)
        if form.is_valid():
            # تخصيص form بـ basic_info
            employee_job_title = form.save(commit=False)
            employee_job_title.basic_info = basic_info
            employee_job_title.save()
            return redirect('hrhub:main_employee_job_title')  # تغيير إلى URL مناسب
    else:
        form = EmployeeJobTitleForm()


    return render(request, 'hrhub/jobtitle/employee_job_title/create_employee_job_title.html', {'form': form, 'basic_info': basic_info})



from django.shortcuts import get_object_or_404, render, redirect



import csv
from django.http import HttpResponse
import csv
from django.http import HttpResponse

def download_sample_employee_job_title_csv(request):
    # إعداد الاستجابة ليتم تحميلها كملف CSV مع الترميز المناسب لدعم اللغة العربية
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="employee_job_title_sample.csv"'

    # إعداد كاتب CSV مع الترميز المناسب
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة عناوين الأعمدة باللغة العربية
    header = [
        'الموظف', 'حساب العنوان الوظيفي تلقائيًا', 'العنوان الوظيفي عند التعيين',
        'تاريخ الحصول على العنوان الوظيفي', 'العنوان الوظيفي الحالي', 
        'تاريخ الحصول على العنوان الوظيفي الحالي', 'العنوان الوظيفي القادم',
        'تاريخ الحصول على العنوان الوظيفي القادم', 'الملاحظات', 'تم الإنشاء بواسطة', 
        'معتمد'
    ]
    writer.writerow(header)

    # إضافة معطيات نموذجية
    sample_rows = [
        ['78013019700', 'نعم', 'مهندس', '2023-01-01', 'مدير', '2024-01-01', 'مدير أعلى', '2025-01-01', '', 'اسم المستخدم', 'لا'],
    ]
    writer.writerows(sample_rows)

    return response



import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

from datetime import datetime
import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages

from datetime import datetime

import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


from datetime import datetime

import csv
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden

# دالة لتحويل التاريخ إلى التنسيق المطلوب
def parse_date(date_string):
    date_formats = ["%d/%m/%Y", "%Y-%m-%d"]  # تنسيقات التاريخ المقبولة
    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            continue
    return None  # إذا لم يتطابق مع أي تنسيق

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.dateparse import parse_date

# دالة لتحويل النص
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.dateparse import parse_date
from datetime import datetime

# دالة لتحويل النصوص إلى تاريخ بشكل آمن
from datetime import datetime

def format_date(date_str):
    """
    تقوم هذه الدالة بتحويل تاريخ مدخل إلى تنسيق موحد (YYYY-MM-DD)
    بعد التحقق من عدة تنسيقات مدعومة.
    """
    date_formats = [
        "%Y-%m-%d",    # تنسيق السنة-الشهر-اليوم
        "%d/%m/%Y",    # تنسيق اليوم/الشهر/السنة
        "%m-%d-%Y",    # تنسيق الشهر-اليوم-السنة
        "%d-%m-%Y",    # تنسيق اليوم-الشهر-السنة
        "%Y/%m/%d",    # تنسيق السنة/الشهر/اليوم
        "%B %d, %Y",   # تنسيق الشهر الكامل اليوم, السنة (مثل: January 01, 2025)
        "%b %d, %Y"    # تنسيق الشهر المختصر اليوم, السنة (مثل: Jan 01, 2025)
    ]
    
    for date_format in date_formats:
        try:
            # محاولة تحويل التاريخ إلى كائن datetime
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date.strftime("%Y-%m-%d")  # إرجاع التاريخ بالتنسيق الموحد
        except ValueError:
            continue  # إذا فشل التحويل، حاول التنسيق التالي
    
    # إذا لم يتمكن من تحويل التاريخ، أعد قيمة فارغة أو خطأ
    return None  # أو يمكنك رفع استثناء هنا إذا أردت
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from datetime import datetime


# دالة لتحويل النص إلى تاريخ مع التحقق من صحة التنسيق
def parse_safe_date(date_str):
    try:
        # محاولة تفسير التواريخ المختلفة مع تنسيقات متعددة
        if date_str:
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            return None  # إذا لم تتطابق مع أي تنسيق
        return None
    except Exception as e:
        return None
    
@login_required
@permission_required('hrhub.can_add_employee_job_title', raise_exception=True)
def upload_employee_job_title_csv(request):
    
    if request.method == 'POST':
        form = EmployeeJobTitleCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                # قراءة الملف وفك ترميزه
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.reader(decoded_file)

                # تخطي الصف الأول (عناوين الأعمدة)
                next(reader)

                for row in reader:
                    try:
                        # قراءة البيانات من الأعمدة
                        emp_username = row[0].strip() if row[0].strip() else None
                        auto_upgrade = row[1].strip() == 'نعم'  # تحويل الإجابة إلى Boolean
                        start_job_title = row[2].strip() if row[2].strip() else None
                        start_date_str = row[3].strip()  # التاريخ كنص خام
                        current_job_title = row[4].strip() if row[4].strip() else None
                        current_job_date_str = row[5].strip()  # التاريخ كنص خام
                        next_job_title = row[6].strip() if row[6].strip() else None
                        next_job_date_str = row[7].strip()  # التاريخ كنص خام
                        comments = row[8].strip() if row[8].strip() else None
                        created_by = row[9].strip() if row[9].strip() else None
                        is_approved = row[10].strip() == 'نعم'

                        # تحويل النصوص إلى تواريخ إذا كانت موجودة
                        start_date = parse_safe_date(start_date_str) if start_date_str else None
                        current_job_date = parse_safe_date(current_job_date_str) if current_job_date_str else None
                        next_job_date = parse_safe_date(next_job_date_str) if next_job_date_str else None

                        # التأكد من أن start_date هو قيمة صحيحة (وعدم تركه غير معرف)
                        if start_date_str and start_date is None:
                            messages.error(request, f"التاريخ {start_date_str} غير صالح في السطر {row}.")
                            continue

                        # التأكد من أن current_job_date هو قيمة صحيحة
                        if current_job_date_str and current_job_date is None:
                            messages.error(request, f"التاريخ {current_job_date_str} غير صالح في السطر {row}.")
                            continue

                        # التأكد من أن next_job_date هو قيمة صحيحة
                        if next_job_date_str and next_job_date is None:
                            messages.error(request, f"التاريخ {next_job_date_str} غير صالح في السطر {row}.")
                            continue

                        # جلب الموظف وJobTitle المرتبطة به
                        try:
                            emp = Employee.objects.get(username=emp_username)
                            start_job_title_obj = JobTitle.objects.filter(title_in_arabic=start_job_title).first() if start_job_title else None
                            current_job_title_obj = JobTitle.objects.filter(title_in_arabic=current_job_title).first() if current_job_title else None
                            next_job_title_obj = JobTitle.objects.filter(title_in_arabic=next_job_title).first() if next_job_title else None
                        except Employee.DoesNotExist:
                            messages.error(request, f"الموظف برقم وظيفي {emp_username} غير موجود.")
                            continue
                        except JobTitle.DoesNotExist:
                            messages.error(request, f"العنوان الوظيفي {start_job_title} أو {current_job_title} أو {next_job_title} غير موجود.")
                            continue

                        # إنشاء أو تحديث السجل
                        employee_job_title, created = EmployeeJobTitle.objects.update_or_create(
                            basic_info=emp.basic_info,
                            defaults={
                                'auto_Employeee_upgrade': auto_upgrade,
                                'start_employee_job_title': start_job_title_obj,
                                'start_employee_job_title_date': start_date,
                                'employee_job_title': current_job_title_obj,
                                'employee_job_title_date': current_job_date,
                                'next_employee_job_title': next_job_title_obj,
                                'next_employee_job_title_date': next_job_date,
                                'comments': comments,
                                'created_by': request.user if isinstance(request.user, Employee) else None,
                                'is_approved': is_approved,
                            }
                        )
                    except Exception as e:
                        messages.error(request, f"خطأ أثناء معالجة السطر {row}: {str(e)}")
                        continue

                # رسالة نجاح
                messages.success(request, "تم تحميل البيانات بنجاح!")
                return redirect('hrhub:main_employee_job_title')  # اذهب إلى الصفحة المناسبة بعد النجاح
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء قراءة الملف: {str(e)}")
    else:
        form = EmployeeJobTitleCSVUploadForm()

    return render(request, 'hrhub/jobtitle/employee_job_title/upload_employee_job_title_csv.html', {'form': form})





from hrhub.forms.JobForm import JobTitleCSVUploadForm


import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify

@login_required
@permission_required('hrhub.can_add_employee_job_title', raise_exception=True)
def upload_job_titles_csv(request):
    if request.method == 'POST':
        form = JobTitleCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # قراءة محتوى الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                # قراءة جميع البيانات في قائمة
                rows = []
                for row in reader:
                    title = row.get('العنوان الوظيفي', '').strip()
                    parent_title = row.get('العنوان الوظيفي الأعلى', '').strip()
                    description = row.get('الوصف', '').strip() if row.get('الوصف') else None

                    if not title:
                        messages.error(request, f"اسم العنوان الوظيفي مفقود في السطر: {row}.")
                        continue

                    rows.append({'title': title, 'parent_title': parent_title, 'description': description})

                # معالجة العناوين الوظيفية العليا أولاً
                for row in rows:
                    parent_title = row['parent_title']
                    if parent_title:  # إذا كان العنوان الوظيفي الأعلى موجودًا
                        JobTitle.objects.get_or_create(
                            title_in_arabic=parent_title,
                            defaults={'slug': slugify(unidecode(parent_title))}
                        )

                # معالجة العناوين الوظيفية الفرعية
                for row in rows:
                    title = row['title']
                    parent_title = row['parent_title']
                    description = row['description']

                    parent = None
                    if parent_title:
                        parent = JobTitle.objects.filter(title_in_arabic=parent_title).first()

                    # إنشاء أو تحديث العنوان الوظيفي
                    JobTitle.objects.update_or_create(
                        title_in_arabic=title,
                        defaults={
                            'parent': parent,
                            'description': description,
                            'slug': slugify(unidecode(title))
                        }
                    )

                messages.success(request, "تم تحميل البيانات وربط العناوين الوظيفية بنجاح!")
                return redirect('hrhub:main_employee_job_title')  # استبدل `job_titles_list` بالمسار الصحيح
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = JobTitleCSVUploadForm()

    return render(request, 'hrhub/jobtitle/upload_job_titles_csv.html', {'form': form})



from hrhub.forms.JobForm import EmployeeJobTitleCSVUploadForm



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
@permission_required('hrhub.can_add_employee_job_title', raise_exception=True)
def upload_employee_job_titles_csv(request):
    if request.method == 'POST':
        form = EmployeeJobTitleCSVUploadForm(request.POST, request.FILES)
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
                        start_job_title_name = row.get('العنوان الوظيفي عند التعيين', '').strip()
                        start_job_title_date_str = row.get('تاريخ الحصول على العنوان الوظيفي عند التعيين', '').strip()
                        current_job_title_name = row.get('العنوان الوظيفي الحالي', '').strip()
                        current_job_title_date_str = row.get('تاريخ الحصول على العنوان الوظيفي الحالي', '').strip()
                        next_job_title_name = row.get('العنوان الوظيفي القادم', '').strip()
                        next_job_title_date_str = row.get('تاريخ الحصول على العنوان الوظيفي القادم', '').strip()
                        auto_upgrade = row.get('احتساب العنوان تلقائياً', '').strip().lower() == 'نعم'
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        start_job_title_date = parse_date(start_job_title_date_str)
                        current_job_title_date = parse_date(current_job_title_date_str)
                        next_job_title_date = parse_date(next_job_title_date_str)

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not start_job_title_name or not start_job_title_date:
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

                        # ✅ البحث عن العناوين الوظيفية أو إنشاؤها
                        start_job_title, _ = JobTitle.objects.get_or_create(
                            title_in_arabic=start_job_title_name
                        )
                        current_job_title = JobTitle.objects.filter(title_in_arabic=current_job_title_name).first() if current_job_title_name else None
                        next_job_title = JobTitle.objects.filter(title_in_arabic=next_job_title_name).first() if next_job_title_name else None

                        # ✅ إنشاء سجل EmployeeJobTitle
                        EmployeeJobTitle.objects.create(
                            basic_info=basic_info,
                            auto_Employeee_upgrade=auto_upgrade,
                            start_employee_job_title=start_job_title,
                            start_employee_job_title_date=start_job_title_date,
                            employee_job_title=current_job_title,
                            employee_job_title_date=current_job_title_date,
                            next_employee_job_title=next_job_title,
                            next_employee_job_title_date=next_job_title_date,
                            comments=comments
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات العناوين الوظيفية بنجاح!")
                return redirect('hrhub:main_employee_job_title')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeJobTitleCSVUploadForm()

    return render(request, 'hrhub/jobtitle/employee_job_title/upload_employee_job_titles_csv.html', {'form': form})



def update_employee_job_title_settings(request):
    settings_instance, created = EmployeeJobTitleSettings.objects.get_or_create(pk=1)  # ضمان وجود سجل واحد فقط

    if request.method == 'POST':
        form = EmployeeJobTitleSettingsForm(request.POST, instance=settings_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الإعدادات بنجاح.")
            return redirect('hrhub:main_employee_job_title')  # إعادة التوجيه إلى نفس الصفحة بعد الحفظ
    else:
        form = EmployeeJobTitleSettingsForm(instance=settings_instance)

    return render(request, 'hrhub/jobtitle/employee_job_title/job_title_setting.html', {'form': form})