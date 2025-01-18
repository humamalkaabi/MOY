from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from hrhub.forms.thanks_punishments import AbsenceTypeForm
from hrhub.models.thanks_punishment_absence_models import AbsenceType

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
def main_absence_type(request):
    absence_types = AbsenceType.objects.all()
    return render(request, 'hrhub/absence/main_absence_type.html', {'absence_types': absence_types})

@login_required
@permission_required('hrhub.can_add_absence_type', raise_exception=True)
def add_absence_type(request):
    if request.method == 'POST':
        form = AbsenceTypeForm(request.POST)
        if form.is_valid():
            absence_type = form.save(commit=False)
            absence_type.created_by = request.user  # تعيين المستخدم الحالي
            absence_type.save()
            messages.success(request, "تم إضافة نوع الغياب بنجاح!")
            return redirect('hrhub:main_absence_type')
        else:
            messages.error(request, "حدث خطأ أثناء إضافة نوع الغياب. يرجى المحاولة مرة أخرى.")
    else:
        form = AbsenceTypeForm()

    return render(request, 'hrhub/absence/add_absence_type.html', {'form': form})

# عرض تفاصيل السجل
@login_required
def absence_type_detail(request, slug):
    absence_type = get_object_or_404(AbsenceType, slug=slug)
    return render(request, 'hrhub/absence/absence_type_detail.html', {'absence_type': absence_type})

@login_required
@permission_required('hrhub.can_update_absence_type', raise_exception=True)
def update_absence_type(request, slug):
    absence_type = get_object_or_404(AbsenceType, slug=slug)
    if request.method == 'POST':
        form = AbsenceTypeForm(request.POST, instance=absence_type)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث نوع الغياب بنجاح!")
            return redirect('hrhub:main_absence_type')
        else:
            messages.error(request, "حدث خطأ أثناء تحديث نوع الغياب. يرجى المحاولة مرة أخرى.")
    else:
        form = AbsenceTypeForm(instance=absence_type)

    return render(request, 'hrhub/absence/update_absence_type.html', {'form': form})

# حذف سجل
@login_required
@permission_required('hrhub.can_delete_absence_type', raise_exception=True)
def delete_absence_type(request, slug):
    absence_type = get_object_or_404(AbsenceType, slug=slug)
    absence_type.delete()
    messages.success(request, "تم حذف نوع الغياب بنجاح!")
    return redirect('hrhub:main_absence_type')







###################### Absences
from personalinfo.models import BasicInfo
from hrhub.models.thanks_punishment_absence_models import EmployeeAbsence
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db.models import Q 
from accounts.models import Employee 
from django.db.models import Count, Case, When, BooleanField
 
@login_required
def main_absences_employee(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_absence = request.GET.get('has_absence', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    absence_type_query = request.GET.get('absence_type', '')  
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
    
    if has_absence:  # إضافة شرط البحث عن الغياب
        if has_absence.lower() == 'yes':
            query &= Q(basic_info__employee_absence_recipients__isnull=False)  # الموظفون الذين لديهم غياب
        elif has_absence.lower() == 'no':
            query &= Q(basic_info__employee_absence_recipients__isnull=True)  # الموظفون الذين 
            
    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)
    
    if absence_type_query:  # تصفية استنادًا إلى نوع الغياب
        query &= Q(basic_info__employee_absence_recipients__absence_type_id=absence_type_query)
    
    
    

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query).distinct()
    # تجميع الموظفين الذين لديهم غياب لتجنب التكرار
    if has_absence.lower() == 'yes':
        employees = employees.annotate(absence_count=Count('basic_info__employee_absence_recipients')).filter(absence_count__gt=0)
    absence_types = AbsenceType.objects.all()
    

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

    return render(request, 'hrhub/absence/main_absences_employee.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'absence_types': absence_types,
    })


from hrhub.forms.thanks_punishments import EmployeeAbsenceForm

@login_required
@permission_required('hrhub.can_add_employee_absence', raise_exception=True)
def add_absence_to_employees(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist('selected_employees')
        selected_employees = BasicInfo.objects.filter(id__in=selected_ids)
        if not selected_employees.exists():
            messages.error(request, "لم يتم اختيار أي موظف.")
            return redirect('hrhub:main_absences_employee')
        return render(request, 'hrhub/absence/add_absence_form.html', {
            'selected_employees': selected_employees,
            'form': EmployeeAbsenceForm(),
        })
    return redirect('hrhub:main_absences_employee')

def save_absence(request):
    if request.method == "POST":
        form = EmployeeAbsenceForm(request.POST)
        selected_ids = request.POST.getlist('selected_employees')
        selected_employees = BasicInfo.objects.filter(id__in=selected_ids)
        if form.is_valid():
            for employee in selected_employees:
                absence = form.save(commit=False)
                absence.created_by = request.user
                absence.save()
                absence.emp_id_absence.add(employee)
            messages.success(request, "تم إضافة الغياب للموظفين بنجاح.")
            return redirect('hrhub:main_absences_employee')
    messages.error(request, "حدث خطأ أثناء إضافة الغياب.")
    return redirect('hrhub:main_absences_employee')




@login_required
def employee_absence_list(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)
    absences = EmployeeAbsence.objects.filter(emp_id_absence=employee)

    return render(request, 'hrhub/absence/employee_absence_list.html', {'employee': employee, 'absences': absences})



@login_required
def employee_absence_listemployee(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع أنواع الغياب لعرضها في القائمة المنسدلة
    absence_types = AbsenceType.objects.all()

    # استلام نوع الغياب المحدد من طلب GET
    selected_absence_type = request.GET.get('absence_type', '')

    # تصفية الغيابات بناءً على النوع المحدد
    absences = EmployeeAbsence.objects.filter(emp_id_absence=employee)
    if selected_absence_type:
        absences = absences.filter(absence_type_id=selected_absence_type)

    # حساب عدد سجلات الغياب بعد التصفية
    absences_count = absences.count()

    return render(request, 'hrhub/absence/employee_absence_listemployee.html', {
        'employee': employee,
        'absences': absences,
        'absence_types': absence_types,
        'selected_absence_type': selected_absence_type,
        'absences_count': absences_count,  # عدد الغيابات لعرضه في القائمة الجانبية
    })



@login_required
def absence_detail(request, slug):
    # جلب سجل الغياب باستخدام الـ slug
    absence = get_object_or_404(EmployeeAbsence, slug=slug)
    
    # تمرير السجل إلى القالب
    return render(request, 'hrhub/absence/absence_detail.html', {'absence': absence})


@login_required
@permission_required('hrhub.can_delete_employee_absence', raise_exception=True)
def delete_absence(request, slug):
  
    # جلب سجل الغياب
    absence = get_object_or_404(EmployeeAbsence, slug=slug)
    
    # حذف السجل
    absence.delete()
    
    # رسالة نجاح وإعادة التوجيه
    messages.success(request, "تم حذف سجل الغياب بنجاح.")
    return redirect('hrhub:main_absences_employee')

@login_required
@permission_required('hrhub.can_update_employee_absence', raise_exception=True)
def update_absence(request, slug):
    absence = get_object_or_404(EmployeeAbsence, slug=slug)

    if request.method == 'POST':
        form = EmployeeAbsenceForm(request.POST, request.FILES, instance=absence)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث سجل الغياب بنجاح.")
            return redirect('hrhub:main_absences_employee')
        else:
            messages.error(request, "حدث خطأ أثناء تحديث السجل. يرجى المحاولة مرة أخرى.")
    else:
        form = EmployeeAbsenceForm(instance=absence)

    context = {
        'form': form,
        'absence': absence,
    }
    return render(request, 'hrhub/absence/update_absence.html', context)




import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from hrhub.forms.thanks_punishments import EmployeeAbsenceCSVUploadForm

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
@permission_required('hrhub.can_add_employee_absence', raise_exception=True)
def upload_employee_absence_csv(request):
    if request.method == 'POST':
        form = EmployeeAbsenceCSVUploadForm(request.POST, request.FILES)
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
                        absence_type_name = row.get('نوع الغياب', '').strip()
                        absence_number = row.get('رقم كتاب الغياب', '').strip()
                        date_issued_str = row.get('تاريخ صدور الامر', '').strip()
                        start_date_str = row.get('تاريخ بداية الغياب', '').strip()
                        end_date_str = row.get('تاريخ نهاية الغياب', '').strip()
                        duration_years = row.get('مدة الغياب بالسنوات', '').strip() or None
                        duration_months = row.get('مدة الغياب بالشهور', '').strip() or None
                        duration_days = row.get('مدة الغياب بالأيام', '').strip() or None
                        approved = row.get('موافق عليه', '').strip().lower() == 'نعم'
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        date_issued = parse_date(date_issued_str)
                        start_date = parse_date(start_date_str)
                        end_date = parse_date(end_date_str)

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not absence_type_name or not absence_number or not date_issued or not start_date or not end_date:
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

                        # ✅ البحث عن نوع الغياب أو إنشاؤه
                        absence_type, _ = AbsenceType.objects.get_or_create(
                            absence_name=absence_type_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ إنشاء slug فريد
                        slug_base = f"{absence_type.absence_name} - {absence_number}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while EmployeeAbsence.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء سجل EmployeeAbsence
                        employee_absence = EmployeeAbsence.objects.create(
                            created_by=request.user,
                            absence_type=absence_type,
                            absence_number=absence_number,
                            date_issued=date_issued,
                            start_date=start_date,
                            end_date=end_date,
                            duration_years=int(duration_years) if duration_years else None,
                            duration_months=int(duration_months) if duration_months else None,
                            duration_days=int(duration_days) if duration_days else None,
                            approved=approved,
                            comments=comments,
                            slug=unique_slug
                        )

                        # ✅ ربط الموظف بكتاب الغياب
                        employee_absence.emp_id_absence.add(basic_info)

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات الغياب بنجاح!")
                return redirect('hrhub:main_absences_employee')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeAbsenceCSVUploadForm()

    return render(request, 'hrhub/absence/upload_employee_absence_csv.html', {'form': form})




import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def download_employee_absence_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="employee_absence_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الرقم الوظيفي', 'نوع الغياب', 'رقم كتاب الغياب', 'تاريخ صدور الامر', 'تاريخ بداية الغياب', 'تاريخ نهاية الغياب', 'مدة الغياب بالسنوات', 'مدة الغياب بالشهور', 'مدة الغياب بالأيام', 'موافق عليه', 'ملاحظات']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        ['78000000045', 'غياب', 'G-1001', '01/01/2024', '05/01/2024', '10/01/2024', '0', '0', '5', 'نعم', '  معتمدة'],
       
    ]
    writer.writerows(example_rows)

    return response
