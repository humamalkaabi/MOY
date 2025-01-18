from django.shortcuts import render, get_object_or_404
from personalinfo.models import BasicInfo
from django.db.models import Q


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from hrhub.forms.thanks_punishments import UpdateIsCountedForm

from django.shortcuts import render, get_object_or_404
from personalinfo.models import BasicInfo
from .models.thanks_punishment_absence_models import EmployeePunishment, PunishmentType
from django.db.models import Q

########### Punish 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from hrhub.forms.thanks_punishments import PunishmentTypeForm
from django.contrib import messages
from django.http import HttpResponseForbidden


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied




@login_required
def main_punishment_types(request):
  
    punishment_types = PunishmentType.objects.all()
    return render(request, 'hrhub/punishments/punishment_types/main_punishment_types.html', {'punishment_types': punishment_types})


@login_required
@permission_required('hrhub.can_add_punishment_type', raise_exception=True)
def add_punishment_type(request):
  
    
    if request.method == 'POST':
        form = PunishmentTypeForm(request.POST)
        if form.is_valid():
            punishment_type = form.save(commit=False)
            punishment_type.created_by = request.user
            punishment_type.save()
            messages.success(request, "تم إضافة نوع العقوبة بنجاح.")
            return redirect('hrhub:main_punishment_types')
    else:
        form = PunishmentTypeForm()
    return render(request, 'hrhub/punishments/punishment_types/add_punishment_type.html', {'form': form})

@login_required
def punishment_type_detail(request, slug):
    punishment_type = get_object_or_404(PunishmentType, slug=slug)
    return render(request, 'hrhub/punishments/punishment_types/punishment_type_detail.html', {'punishment_type': punishment_type})



@login_required
@permission_required('hrhub.can_update_punishment_type', raise_exception=True)
def update_punishment_type(request, slug):
    punishment_type = get_object_or_404(PunishmentType, slug=slug)
    if request.method == 'POST':
        form = PunishmentTypeForm(request.POST, instance=punishment_type)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث نوع العقوبة بنجاح.")
            return redirect('hrhub:main_punishment_types')
    else:
        form = PunishmentTypeForm(instance=punishment_type)
    return render(request, 'hrhub/punishments/punishment_types/update_punishment_type.html', {'form': form, 'punishment_type': punishment_type})



@login_required
@permission_required('hrhub.can_delete_punishment_type', raise_exception=True)
def delete_punishment_type(request, slug):
    
    
    punishment_type = get_object_or_404(PunishmentType, slug=slug)
    punishment_type.delete()
    messages.success(request, "تم حذف نوع العقوبة بنجاح.")
    return redirect('hrhub:main_punishment_types')


############ Employee 
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from accounts.models import Employee

@login_required
def main_employee_punishments(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_punishment = request.GET.get('has_punishment', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    punishment_type_query = request.GET.get('punishment_type', '')
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
    if has_punishment:
        if has_punishment.lower() == 'yes':
            # الموظف لديه عقوبات
            query &= Q(basic_info__employee_punishment_recipients__isnull=False)
        elif has_punishment.lower() == 'no':
            # الموظف ليس لديه عقوبات
            query &= Q(basic_info__employee_punishment_recipients__isnull=True)



    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    if punishment_type_query:
        query &= Q(basic_info__employee_punishment_recipients__punishment_type__id=punishment_type_query)

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query).distinct()
    punishment_types = PunishmentType.objects.all()
    

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

    return render(request, 'hrhub/punishments/employee_punishments/main_employee_punishments.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'punishment_types': punishment_types,
        'results_per_page': results_per_page,
    })


from hrhub.forms.thanks_punishments import EmployeePunishmentForm


@login_required
@permission_required('hrhub.can_add_employee_punishment', raise_exception=True)
def add_punishments_to_employees(request):
    if request.method == "POST":
        selected_slugs = request.POST.getlist('selected_employees')  # جلب slugs المختارة
        print("Selected Slugs:", selected_slugs)

        selected_employees = BasicInfo.objects.filter(slug__in=selected_slugs)
        print("Selected Employees QuerySet:", selected_employees)

        if not selected_employees.exists():
            messages.error(request, "لم يتم اختيار أي موظف.")
            return redirect('hrhub:main_employee_punishments')  # العودة إلى صفحة البحث

        return render(request, 'hrhub/punishments/employee_punishments/add_punishment_form.html', {
            'selected_employees': selected_employees,
            'form': EmployeePunishmentForm(),
        })
    return redirect('hrhub:main_employee_punishments')




def save_punishments(request):
    if request.method == "POST":
        form = EmployeePunishmentForm(request.POST, request.FILES)
        selected_slugs = request.POST.getlist('selected_employees')  # جلب slugs المختارة
        selected_employees = BasicInfo.objects.filter(slug__in=selected_slugs)

        if form.is_valid():
            for employee in selected_employees:
                punishment = form.save(commit=False)
                punishment.created_by = request.user
                punishment.save()
                punishment.emp_id_punishment.add(employee)
            messages.success(request, "تم إضافة العقوبات للموظفين بنجاح.")
            return redirect('hrhub:main_employee_punishments')  # العودة إلى صفحة البحث
    messages.error(request, "حدث خطأ أثناء إضافة العقوبات.")
    return redirect('hrhub:main_employee_punishments')




@login_required
def employee_punishments_list(request, slug):
    # الحصول على الموظف باستخدام slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع العقوبات المرتبطة بالموظف
    punishments = EmployeePunishment.objects.filter(emp_id_punishment=employee)

    context = {
        'employee': employee,
        'punishments': punishments,
    }
    return render(request, 'hrhub/punishments/employee_punishments/employee_punishments_list.html', context)



@login_required
def employee_punishments_listemployee(request, slug):
    # الحصول على الموظف باستخدام slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع أنواع العقوبات لعرضها في القائمة المنسدلة
    punishment_types = PunishmentType.objects.all()

    # استلام نوع العقوبة المحدد من طلب GET
    selected_punishment_type = request.GET.get('punishment_type', '')

    # تصفية العقوبات بناءً على النوع المحدد
    punishments = EmployeePunishment.objects.filter(emp_id_punishment=employee)
    if selected_punishment_type:
        punishments = punishments.filter(punishment_type_id=selected_punishment_type)

    # حساب عدد العقوبات بعد التصفية
    punishments_count = punishments.count()

    context = {
        'employee': employee,
        'punishments': punishments,
        'punishment_types': punishment_types,
        'selected_punishment_type': selected_punishment_type,
        'punishments_count': punishments_count,  # عدد العقوبات لعرضه في القائمة الجانبية
    }
    return render(request, 'hrhub/punishments/employee/employee_punishments_listemployee.html', context)






@login_required
@permission_required('hrhub.can_update_employee_punishment', raise_exception=True)
def update_employee_punishment(request, slug):
    # جلب كتاب العقوبة باستخدام الـ slug
    punishment = get_object_or_404(EmployeePunishment, slug=slug)

    if request.method == 'POST':
        form = EmployeePunishmentForm(request.POST, request.FILES, instance=punishment)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث كتاب العقوبة بنجاح.")
            return redirect('hrhub:main_employee_punishments')
    else:
        form = EmployeePunishmentForm(instance=punishment)

    return render(request, 'hrhub/punishments/employee_punishments/update_employee_punishment.html', {'form': form, 'punishment': punishment})


@login_required
@permission_required('hrhub.can_delete_employee_punishment', raise_exception=True)
def delete_employee_punishment(request, slug):
   
    punishment = get_object_or_404(EmployeePunishment, slug=slug)

    # حذف كتاب العقوبة
    punishment.delete()

    # رسالة نجاح وإعادة التوجيه
    messages.success(request, "تم حذف كتاب العقوبة بنجاح.")
    return redirect('hrhub:main_employee_punishments')




import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from hrhub.forms.thanks_punishments import EmployeePunishmentCSVUploadForm

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
@permission_required('hrhub.can_add_employee_punishment', raise_exception=True)
def upload_employee_punishment_csv(request):
    if request.method == 'POST':
        form = EmployeePunishmentCSVUploadForm(request.POST, request.FILES)
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
                        punishment_type_name = row.get('نوع العقوبة', '').strip()
                        punishment_number = row.get('رقم كتاب العقوبة', '').strip()
                        date_issued_str = row.get('تاريخ إصدار كتاب العقوبة', '').strip()
                        is_counted = row.get('يتم احتسابه', '').strip().lower() == 'نعم'
                        approved = row.get('موافق عليه', '').strip().lower() == 'نعم'
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التاريخ إلى تنسيق صحيح
                        date_issued = parse_date(date_issued_str)

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not punishment_type_name or not punishment_number or not date_issued:
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

                        # ✅ البحث عن نوع العقوبة أو إنشاؤه
                        punishment_type, _ = PunishmentType.objects.get_or_create(
                            punishment_name=punishment_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ إنشاء slug فريد
                        slug_base = f"{punishment_type.punishment_name} - {punishment_number}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while EmployeePunishment.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء سجل EmployeePunishment
                        employee_punishment = EmployeePunishment.objects.create(
                            created_by=request.user,
                            punishment_type=punishment_type,
                            punishment_number=punishment_number,
                            date_issued=date_issued,
                            is_counted=is_counted,
                            approved=approved,
                            comments=comments,
                            slug=unique_slug
                        )

                        # ✅ ربط الموظف بكتاب العقوبة
                        employee_punishment.emp_id_punishment.add(basic_info)

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات كتب العقوبات بنجاح!")
                return redirect('hrhub:main_employee_punishments')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeePunishmentCSVUploadForm()

    return render(request, 'hrhub/punishments/employee_punishments/upload_employee_punishment_csv.html', {'form': form})


from django.http import HttpResponse


def download_punishment_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="punishment_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الرقم الوظيفي', 'نوع العقوبة', 'رقم كتاب العقوبة', 'تاريخ إصدار كتاب العقوبة', 'يتم احتسابه', 'موافق عليه', 'ملاحظات']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        [78000000045, 'عقوبة', 1001, '15/01/2024', 'نعم', 'نعم', 'تأخر متكرر'],
        [78000000046, 'عقوبة', 1001, '16/01/2024', 'نعم', 'نعم', ''],
        [78000000047, 'عقوبة', 1001, '17/01/2024', 'نعم', 'نعم', ''],
        [78000000048, 'عقوبة', 1001, '18/01/2024', 'نعم', 'نعم', ''],
        [78000000049, 'عقوبة', 1001, '19/01/2024', 'نعم', 'نعم', '']
    ]
    writer.writerows(example_rows)

    return response
