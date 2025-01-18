from django.shortcuts import render, get_object_or_404
from personalinfo.models import BasicInfo
from django.db.models import Q

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from personalinfo.models import BasicInfo
from .models.thanks_punishment_absence_models import EmployeeThanks, ThanksType
from django.db.models import Q
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied




@login_required
def main_thanks_type(request):
    
    
    thanks_types = ThanksType.objects.all()
    
    
    context = {
        'thanks_types': thanks_types,
        'thanks_types_count': thanks_types.count
    }

    return render(request, 'hrhub/thanks/thankstype/main_thanks_type.html', context)


from hrhub.forms.thanks_punishments import ThanksTypeForm



@login_required
@permission_required('hrhub.can_add_thanks_type', raise_exception=True)
def add_thanks_type(request):
    # التحقق من الصلاحيات
    
    
    login_user = request.user
    if request.method == 'POST':
        form = ThanksTypeForm(request.POST)
        if form.is_valid():
            # إعداد الكائن قبل الحفظ
            thanks_type = form.save(commit=False)
            thanks_type.created_by = login_user
            thanks_type.save()
            return redirect('hrhub:main_thanks_type')  # عدّل الرابط إذا لزم الأمر
        else:
            messages.error(request, "حدث خطأ أثناء إضافة البيانات . يرجى المحاولة مرة أخرى.")
    else:
        form = ThanksTypeForm()

    # تمرير النموذج والسياق إلى القالب
    return render(request, 'hrhub/thanks/thankstype/add_thanks_type.html', {
        'form': form,
        'login_user': login_user,
    })


@login_required
def thanks_type_detail(request, slug):
    thanks_type = get_object_or_404(ThanksType, slug=slug)
    return render(request, 'hrhub/thanks/thankstype/thanks_type_detail.html', {'thanks_type': thanks_type})

@login_required
@permission_required('hrhub.can_update_thanks_type', raise_exception=True)
def update_thanks_type(request, slug):
    # Retrieve the specific instance using the slug
    thankstype = get_object_or_404(ThanksType, slug=slug)
    
    if request.method == 'POST':
        form = ThanksTypeForm(request.POST, instance=thankstype)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث  الكلية بنجاح!")
            return redirect('hrhub:main_thanks_type')  # Adjust the URL name as needed
        else:
            messages.error(request, "حدث خطأ أثناء تحديث  الكلية. يرجى المحاولة مرة أخرى.")
    else:
        form = ThanksTypeForm(instance=thankstype)
    
    return render(request, 'hrhub/thanks/thankstype/update_thanks_type.html', {
        'form': form,
        'thankstype': thankstype,
    })






@login_required
@permission_required('hrhub.can_delete_thanks_type', raise_exception=True)
def delete_thanks_type(request, slug):
    # التحقق من صلاحيات المستخدم
    if not request.user.has_perm('hrhub.delete_thanks_type'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    thanks_type = get_object_or_404(ThanksType, slug=slug)
    
    thanks_type.delete()
    
    return redirect('hrhub:main_thanks_type')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك




################################### 
from accounts.models import Employee
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from personalinfo.models import BasicInfo
from hrhub.models.office_position_models import Office

@login_required
def main_employeethanks(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_thanks = request.GET.get('has_thanks', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    thanks_type_query = request.GET.get('thanks_type', '')
    office_query = request.GET.get('office', '')  # تصفية حسب الدائرة  # إضافة نوع الشكر
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
    if has_thanks:
        if has_thanks.lower() == 'yes':
            query &= Q(basic_info__thanks_letters__isnull=False)  # الموظف لديه كتب شكر
        elif has_thanks.lower() == 'no':
            query &= Q(basic_info__thanks_letters__isnull=True) 


    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if thanks_type_query:
        query &= Q(basic_info__thanks_letters__thanks_type__id=thanks_type_query)
    
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass  # تصفية حسب نوع الشكر

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query).distinct()
    thanks_types = ThanksType.objects.all()
    offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__parent__isnull=True))  # جلب الدوائر الرئيسية
    

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

    return render(request, 'hrhub/thanks/employee_thanks/main_employeethanks.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'thanks_types': thanks_types,
        'offices': offices,  # تمرير الدوائر إلى القالب
    })



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from django.db.models import Q




from hrhub.forms.thanks_punishments import EmployeeThanksForm


@login_required
@permission_required('hrhub.can_add_employee_thanks', raise_exception=True)
def add_thanks_to_employees(request):
    if request.method == "POST":
        selected_slugs = request.POST.getlist('selected_employees')  # جلب slugs المختارة
        print("Selected Slugs:", selected_slugs)

        selected_employees = BasicInfo.objects.filter(slug__in=selected_slugs)
        print("Selected Employees QuerySet:", selected_employees)

        if not selected_employees.exists():
            messages.error(request, "لم يتم اختيار أي موظف.")
            return redirect('hrhub:main_employeethanks')  # العودة إلى صفحة البحث

        return render(request, 'hrhub/thanks/employee_thanks/add_thanks_form.html', {
            'selected_employees': selected_employees,
            'form': EmployeeThanksForm(),
        })
    return redirect('hrhub:main_employeethanks')


def save_thanks(request):
    if request.method == "POST":
        form = EmployeeThanksForm(request.POST, request.FILES)
        selected_ids = request.POST.getlist('selected_employees')
        selected_employees = BasicInfo.objects.filter(id__in=selected_ids)
        if form.is_valid():
            for employee in selected_employees:
                thanks = form.save(commit=False)
                thanks.created_by = request.user
                thanks.save()
                thanks.emp_id_thanks.add(employee)
            messages.success(request, "تم إضافة كتب الشكر للموظفين بنجاح.")
            return redirect('hrhub:main_employeethanks')  # العودة إلى صفحة البحث
    messages.error(request, "حدث خطأ أثناء إضافة كتب الشكر.")
    return redirect('hrhub:main_employeethanks')

@login_required
def employee_thanks_list(request, slug):
    # الحصول على الموظف باستخدام slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع كتب الشكر المرتبطة بالموظف
    thanks_letters = EmployeeThanks.objects.filter(emp_id_thanks=employee)

    context = {
        'employee': employee,
        'thanks_letters': thanks_letters,
    }
    return render(request, 'hrhub/thanks/employee_thanks/employee_thanks_list.html', context)



@login_required
def employee_thanks_listemployee(request, slug):
    # الحصول على الموظف باستخدام slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع أنواع كتب الشكر لعرضها في القائمة المنسدلة
    thanks_types = ThanksType.objects.all()

    # استلام نوع كتاب الشكر المحدد من طلب GET
    selected_thanks_type = request.GET.get('thanks_type', '')

    # تصفية كتب الشكر بناءً على النوع المحدد
    thanks_letters = EmployeeThanks.objects.filter(emp_id_thanks=employee)
    if selected_thanks_type:
        thanks_letters = thanks_letters.filter(thanks_type_id=selected_thanks_type)

    # حساب عدد النتائج بعد التصفية
    thanks_count = thanks_letters.count()

    context = {
        'employee': employee,
        'thanks_letters': thanks_letters,
        'thanks_types': thanks_types,
        'selected_thanks_type': selected_thanks_type,
        'thanks_count': thanks_count,  # عدد كتب الشكر لعرضه في القائمة الجانبية
    }
    return render(request, 'hrhub/thanks/employee/employee_thanks_listemployee.html', context)



@login_required
@permission_required('hrhub.can_update_employee_thanks', raise_exception=True)
def update_employee_thanks(request, slug):
    # جلب كتاب الشكر باستخدام الـ slug
    thanks = get_object_or_404(EmployeeThanks, slug=slug)

    if request.method == 'POST':
        form = EmployeeThanksForm(request.POST, request.FILES, instance=thanks)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث كتاب الشكر بنجاح.")
            return redirect('hrhub:main_employeethanks')
    else:
        form = EmployeeThanksForm(instance=thanks)

    return render(request, 'hrhub/thanks/employee_thanks/update_employee_thanks.html', {'form': form, 'thanks': thanks})


@login_required
@permission_required('hrhub.can_delete_employee_thanks', raise_exception=True)
def delete_employee_thanks(request, slug):
    # التحقق من الصلاحيات (اختياري)
    # if not request.user.has_perm('hrhub.delete_employeethanks'):
    #     return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")

    # جلب كتاب الشكر باستخدام الـ slug
    thanks = get_object_or_404(EmployeeThanks, slug=slug)

    # حذف كتاب الشكر
    thanks.delete()

    # رسالة نجاح وإعادة التوجيه
    messages.success(request, "تم حذف كتاب الشكر بنجاح.")
    return redirect('hrhub:main_employeethanks')



from hrhub.forms.thanks_punishments import EmployeeThanksCSVUploadForm


import csv
from django.utils.text import slugify
from unidecode import unidecode


import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from accounts.models import Employee
from personalinfo.models import BasicInfo

# دالة لتحويل صيغ التاريخ المختلفة إلى YYYY-MM-DD
def parse_date(date_string):
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None


@login_required
@permission_required('hrhub.can_add_employee_thanks', raise_exception=True)
def upload_employee_thanks_csv(request):
    if request.method == 'POST':
        form = EmployeeThanksCSVUploadForm(request.POST, request.FILES)
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
                        # قراءة البيانات وتحويل القيم
                        emp_id = row.get('الرقم الوظيفي', '').strip()
                        thanks_type_name = row.get('نوع الشكر', '').strip()
                        thanks_number = row.get('رقم كتاب الشكر', '').strip()
                        date_issued_str = row.get('تاريخ إصدار كتاب الشكر', '').strip()
                        is_counted = row.get('يتم احتسابه', '').strip().lower() == 'نعم'
                        approved = row.get('موافق عليه', '').strip().lower() == 'نعم'
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # تحويل التاريخ إلى تنسيق صحيح
                        date_issued = parse_date(date_issued_str)

                        # التحقق من البيانات الأساسية
                        if not emp_id or not thanks_type_name or not thanks_number or not date_issued:
                            messages.error(request, f"بيانات مفقودة أو تنسيق تاريخ غير صحيح في السطر: {row}.")
                            continue

                        # البحث عن الموظف
                        employee = Employee.objects.filter(username=emp_id).first()
                        if not employee:
                            messages.error(request, f"الموظف برقم {emp_id} غير موجود في النظام.")
                            continue

                        # البحث عن BasicInfo للموظف
                        basic_info = BasicInfo.objects.filter(emp_id=employee).first()
                        if not basic_info:
                            messages.error(request, f"لم يتم العثور على بيانات الموظف الأساسية للرقم الوظيفي {emp_id}.")
                            continue

                        # البحث عن نوع الشكر أو إنشاؤه
                        thanks_type, _ = ThanksType.objects.get_or_create(
                            thanks_name=thanks_type_name,
                            defaults={'created_by': request.user}
                        )

                        # إنشاء slug فريد
                        slug_base = f"{thanks_type.thanks_name} - {thanks_number}"
                        unique_slug = slugify(slug_base)

                        count = 1
                        while EmployeeThanks.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(slug_base)}-{count}"
                            count += 1

                        # إنشاء سجل EmployeeThanks
                        employee_thanks = EmployeeThanks.objects.create(
                            created_by=request.user,
                            thanks_type=thanks_type,
                            thanks_number=thanks_number,
                            date_issued=date_issued,
                            is_counted=is_counted,
                            approved=approved,
                            comments=comments,
                            slug=unique_slug
                        )

                        # ربط الموظف بكتاب الشكر
                        employee_thanks.emp_id_thanks.add(basic_info)

                    except Exception as e:
                        messages.error(request, f"حدث خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "تم تحميل بيانات كتب الشكر بنجاح!")
                return redirect('hrhub:main_employeethanks')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeThanksCSVUploadForm()

    return render(request, 'hrhub/thanks/employee_thanks/upload_employee_thanks_csv.html', {'form': form})





def download_thanks_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="thanks_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الرقم الوظيفي', 'نوع الشكر', 'رقم كتاب الشكر', 'تاريخ إصدار كتاب الشكر', 'يتم احتسابه', 'موافق عليه', 'ملاحظات']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        [78000000045, 'شكر', '21dasad', '22/02/2024', 'نعم', '', ''],
        [78000000046, 'شكر', '21dasad', '23/02/2024', 'نعم', '', ''],
        [78000000047, 'شكر', '21dasad', '24/02/2024', 'نعم', '', ''],
        [78000000048, 'شكر', '21dasad', '25/02/2024', 'نعم', '', ''],
        [78000000049, 'شكر', '21dasad', '26/02/2024', 'نعم', '', '']
    ]
    writer.writerows(example_rows)

    return response
