from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from hrhub.models.office_position_models import Office, Position
from hrhub.forms.office_position  import OfficeForm, PositionForm, EmployeeOfficePositionForm, DateRangeForm
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib import messages
from django.utils.translation import gettext as _

from django.shortcuts import render, get_object_or_404
from personalinfo.models import BasicInfo
from .models.office_position_models import EmployeeOfficePosition
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied



import csv
from django.http import HttpResponse



@login_required
def main_position(request):
    
    
    positions = Position.objects.all()

    context = {'positions': positions,
               'positions_count': positions.count}
    return render(request, 'hrhub/office_positions/position/main_position.html', context)



@login_required
@permission_required('hrhub.can_add_position', raise_exception=True)
def add_position(request):
    if not (request.user.has_perm('hrhub.add_position')):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            office = form.save(commit=False)
            office.created_by = request.user
            office.save()
            messages.success(request, "تم إضافة الوحدة الإدارية بنجاح.")
            return redirect('hrhub:main_position')
    else:
        form = PositionForm()
    return render(request, 'hrhub/office_positions/position/add_position.html', {'form': form})



@login_required
def position_detail(request, slug):
    # جلب العنوان الوظيفي المطلوب بناءً على slug
    position = get_object_or_404(Position, slug=slug)

    context = {
        'position': position
    }
    return render(request, 'hrhub/office_positions/position/position_detail.html', context)



@login_required
@permission_required('hrhub.can_update_position', raise_exception=True)
def update_position(request, slug):
    if not (request.user.has_perm('hrhub.change_position')):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    office = get_object_or_404(Position, slug=slug)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=office)
        if form.is_valid():
            office.save()
            messages.success(request, "تم تعديل الوحدة الإدارية بنجاح.")
            return redirect('hrhub:main_position')
    else:
        form = PositionForm(instance=office)
    return render(request, 'hrhub/office_positions/position/update_position.html', {'form': form, 'office': office})



@login_required
@permission_required('hrhub.can_delete_position', raise_exception=True)
def delete_position(request, slug):
    if not (request.user.has_perm('hrhub.delete_position')):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    position = get_object_or_404(Position, slug=slug)
   
    
    position.delete()
    messages.success(request, "تم حذف الوحدة الإدارية بنجاح.")
    return redirect('hrhub:main_position')




######################## office_positions
from personalinfo.models import BasicInfo
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from accounts.models import Employee

@login_required
def main_office_positions(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_office_position = request.GET.get('has_office_position', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    is_primary_position = request.GET.get('is_primary_position', '')
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
    if has_office_position:
        if has_office_position.lower() == 'yes':
            query &= Q(basic_info__employee_office_positions__isnull=False)  # لديه OfficePosition
        elif has_office_position.lower() == 'no':
            query &= Q(basic_info__employee_office_positions__isnull=True)  # ليس لديه OfficePosition


    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)
    if is_primary_position:
        if is_primary_position.lower() == 'yes':
            query &= Q(basic_info__employee_office_positions__is_primary=True)
        elif is_primary_position.lower() == 'no':
            query &= Q(basic_info__employee_office_positions__is_primary=False)

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query).distinct()
    

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

    return render(request, 'hrhub/office_positions/office_positions/main_office_positions.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
    })


from django.shortcuts import render, get_object_or_404, redirect


@login_required
@permission_required('hrhub.can_add_employee_office_position', raise_exception=True)
def add_employee_office_position(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = EmployeeOfficePositionForm(request.POST)
        if form.is_valid():
            office_position = form.save(commit=False)
            office_position.basic_info = employee  # ربط basic_info بالموظف المحدد
            office_position.approved = True  # أو حسب الحاجة
            office_position.created_by = request.user  # تعيين المنشئ
            office_position.save()
            
            return redirect('hrhub:main_office_positions')
    else:
        form = EmployeeOfficePositionForm()

    return render(request, 'hrhub/office_positions/office_positions/add_office_positions.html', {'form': form})

@login_required
def list_employee_office_positions(request, slug):
    # الحصول على الموظف باستخدام slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع المناصب المرتبطة بالموظف
    office_positions = EmployeeOfficePosition.objects.filter(basic_info=employee)

    context = {
        'employee': employee,
        'office_positions': office_positions,
    }
    return render(request, 'hrhub/office_positions/office_positions/list_employee_office_positions.html', context)



@login_required
def list_employee_office_positionsemployee(request, slug):
    # الحصول على الموظف باستخدام slug
    employee = get_object_or_404(BasicInfo, slug=slug)

    # استلام نوع التكليف المحدد من طلب GET
    selected_is_primary = request.GET.get('is_primary', '')

    # جلب جميع المناصب المرتبطة بالموظف
    office_positions = EmployeeOfficePosition.objects.filter(basic_info=employee)

    # تطبيق التصفية حسب نوع التكليف (أصالة أو وكالة)
    if selected_is_primary == 'true':  
        office_positions = office_positions.filter(is_primary=True)
    elif selected_is_primary == 'false':
        office_positions = office_positions.filter(is_primary=False)

    # حساب عدد المناصب بعد التصفية
    office_positions_count = office_positions.count()

    context = {
        'employee': employee,
        'office_positions': office_positions,
        'selected_is_primary': selected_is_primary,
        'office_positions_count': office_positions_count,  # عدد المناصب لعرضه في القائمة الجانبية
    }
    return render(request, 'hrhub/office_positions/office_positions/list_employee_office_positionsemployee.html', context)



from django.shortcuts import render, get_object_or_404

@login_required
def office_position_detail(request, slug):
    # الحصول على المنصب باستخدام slug
    position = get_object_or_404(EmployeeOfficePosition, slug=slug)

    context = {
        'position': position,
    }
    return render(request, 'hrhub/office_positions/office_positions/employee_office_position_detail.html', context)

@login_required
@permission_required('hrhub.can_update_employee_office_position', raise_exception=True)
def update_employee_office_position(request, slug):
    position = get_object_or_404(EmployeeOfficePosition, slug=slug)

    if request.method == 'POST':
        form = EmployeeOfficePositionForm(request.POST, request.FILES, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المنصب بنجاح.")
            return redirect('hrhub:list_employee_office_positions', slug=position.basic_info.slug)
        else:
            messages.error(request, "حدث خطأ أثناء تحديث المنصب. يرجى التحقق من البيانات.")
    else:
        form = EmployeeOfficePositionForm(instance=position)

    context = {
        'form': form,
        'position': position,
    }
    return render(request, 'hrhub/office_positions/office_positions/update_employee_office_position.html', context)


@login_required
@permission_required('hrhub.can_delete_employee_office_position', raise_exception=True)
def delete_employee_office_position(request, slug):
   
    position = get_object_or_404(EmployeeOfficePosition, slug=slug)
    
    # Delete the position
    position.delete()
    messages.success(request, "تم حذف علاقة الموظف بالمكتب والوظيفة بنجاح.")
    
    # Redirect to a relevant page, such as the employee's list of positions
    return redirect('hrhub:list_employee_office_positions', slug=position.basic_info.slug)




import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

@login_required
def export_employee_office_positions_csv(request, slug):
    # Fetch the employee
    employee = get_object_or_404(BasicInfo, slug=slug)
    positions = employee.employee_office_positions.all()
    form = DateRangeForm(request.GET)

    # Apply date range filters if provided
    if form.is_valid():
        if not form.cleaned_data.get('show_all'):
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date:
                positions = positions.filter(start_date__gte=start_date)
            if end_date:
                positions = positions.filter(end_date__lte=end_date)

    # Prepare the CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="employee_office_positions.csv"'

    # Add BOM for Excel compatibility
    response.write('\ufeff'.encode('utf8'))

    # Initialize the CSV writer
    writer = csv.writer(response)

    # Write the CSV headers
    writer.writerow([
        smart_str('الموظف'),
        smart_str('المكتب'),
        smart_str('الوظيفة'),
        smart_str('نوع الأمر الصادر'),
        smart_str(' اصالة'),
        smart_str('تاريخ البدء'),
        smart_str('تاريخ الانتهاء'),
        smart_str('ملاحظات'),
        smart_str('موافق عليه')
    ])

    # Write the data rows
    for position in positions:
        writer.writerow([
            smart_str(position.basic_info),
            smart_str(position.office),
            smart_str(position.position),
            smart_str(position.duty_assignment_order),
            smart_str('نعم' if position.is_primary else 'لا'),
            smart_str(position.start_date),
            smart_str(position.end_date if position.end_date else 'مستمر'),
            smart_str(position.comments),
            smart_str('نعم' if position.approved else 'لا'),
        ])

    return response












import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode
from hrhub.forms.office_position import EmployeeOfficePositionCSVUploadForm
from  hrhub.models.hr_utilities_models import DutyAssignmentOrder
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
@permission_required('hrhub.can_add_employee_office_position', raise_exception=True)
def upload_employee_office_position_csv(request):
    if request.method == 'POST':
        form = EmployeeOfficePositionCSVUploadForm(request.POST, request.FILES)
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
                        office_name = row.get('اسم المكتب', '').strip()
                        position_name = row.get('اسم الوظيفة', '').strip()
                        duty_assignment_order_name = row.get('نوع الأمر الصادر', '').strip()
                        duty_assignment_order_number = row.get('رقم الأمر الصادر', '').strip()
                        duty_assignment_order_date_str = row.get('تاريخ الأمر الصادر', '').strip()
                        start_date_str = row.get('تاريخ المباشرة', '').strip()
                        end_date_str = row.get('تاريخ الانتهاء', '').strip()
                        is_primary = row.get('اصالة', '').strip().lower() == 'نعم'
                        status = row.get('الحالة', '').strip()
                        comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        duty_assignment_order_date = parse_date(duty_assignment_order_date_str) if duty_assignment_order_date_str else None
                        start_date = parse_date(start_date_str) if start_date_str else None
                        end_date = parse_date(end_date_str) if end_date_str else None

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not office_name or not position_name or not duty_assignment_order_name or not start_date:
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

                        # ✅ البحث عن المكتب أو إنشاؤه
                        office, _ = Office.objects.get_or_create(
                            name=office_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ البحث عن الوظيفة أو إنشاؤها
                        position, _ = Position.objects.get_or_create(
                            name=position_name,
                            office=office,
                            defaults={'created_by': request.user}
                        )

                        # ✅ البحث عن نوع الأمر الصادر أو إنشاؤه
                        duty_assignment_order, _ = DutyAssignmentOrder.objects.get_or_create(
                            name_in_arabic=duty_assignment_order_name,
                            defaults={'created_by': request.user}
                        )

                        # ✅ إنشاء slug فريد
                        slug_base = f"{emp_id}-{position_name}-{office_name}"
                        unique_slug = slugify(unidecode(slug_base))

                        count = 1
                        while EmployeeOfficePosition.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                            count += 1

                        # ✅ إنشاء سجل EmployeeOfficePosition
                        employee_office_position = EmployeeOfficePosition.objects.create(
                            basic_info=basic_info,
                            office=office,
                            position=position,
                            duty_assignment_order=duty_assignment_order,
                            duty_assignment_order_number=duty_assignment_order_number,
                            duty_assignment_order_date=duty_assignment_order_date,
                            is_primary=is_primary,
                            start_date=start_date,
                            end_date=end_date,
                            status=status,
                            comments=comments,
                            slug=unique_slug
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات الموظفين والمكاتب والمناصب الوظيفية بنجاح!")
                return redirect('hrhub:main_office_positions')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeOfficePositionCSVUploadForm()

    return render(request, 'hrhub/office_positions/employee/upload_employee_office_position_csv.html', {'form': form})






import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify
from  hrhub.forms.office_position import PositionCSVUploadForm

@login_required
@permission_required('hrhub.can_add_position', raise_exception=True)
def upload_positions_csv(request):
    if request.method == 'POST':
        form = PositionCSVUploadForm(request.POST, request.FILES)
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
                    name = row.get('اسم الوظيفة', '').strip()
                    office_name = row.get('المكتب', '').strip()
                    parent_name = row.get('الوظيفة الأب', '').strip()
                    comments = row.get('ملاحظات', '').strip() if row.get('ملاحظات') else None

                    if not name or not office_name:
                        messages.error(request, f"اسم الوظيفة أو المكتب مفقود في السطر: {row}.")
                        continue

                    rows.append({'name': name, 'office_name': office_name, 'parent_name': parent_name, 'comments': comments})

                # معالجة المكاتب أولاً
                for row in rows:
                    office_name = row['office_name']
                    Office.objects.get_or_create(name=office_name)

                # معالجة المناصب الوظيفية الرئيسية أولاً (التي ليس لديها parent)
                for row in rows:
                    if not row['parent_name']:  # إذا لم يكن لها وظيفة أعلى
                        office = Office.objects.filter(name=row['office_name']).first()
                        Position.objects.get_or_create(
                            name=row['name'],
                            office=office,
                            defaults={'slug': slugify(unidecode(row['name']))}
                        )

                # معالجة المناصب الوظيفية الفرعية وربطها بالمناصب الأب
                for row in rows:
                    if row['parent_name']:
                        office = Office.objects.filter(name=row['office_name']).first()
                        parent_position = Position.objects.filter(name=row['parent_name']).first()
                        Position.objects.update_or_create(
                            name=row['name'],
                            office=office,
                            defaults={
                                'parent': parent_position,
                                'comments': row['comments'],
                                'slug': slugify(unidecode(row['name']))
                            }
                        )

                messages.success(request, "تم تحميل البيانات وربط المناصب الوظيفية بنجاح!")
                return redirect('hrhub:main_position')  # استبدل `positions_list` بالمسار الصحيح
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = PositionCSVUploadForm()

    return render(request, 'hrhub/office_positions/position/upload_positions_csv.html', {'form': form})
