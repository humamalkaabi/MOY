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
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied




@login_required
def main_offices(request):
    # الوحدات الإدارية التي ليس لها دائرة أعلى أو لها دائرة واحدة فقط
    filtered_offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__isnull=False, parent__parent__isnull=True))

    selected_office = request.GET.get('office', '')  # قراءة الوحدة المختارة من الطلب
    results_per_page = request.GET.get('results_per_page', 10)  # القيمة الافتراضية 10

    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:  # التأكد من عدم إدخال قيمة صفر أو أقل
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    offices_list = Office.objects.all()

    # تطبيق التصفية إذا تم اختيار وحدة إدارية
    if selected_office:
        offices_list = offices_list.filter(Q(parent__name=selected_office) | Q(name=selected_office))


    filtered_results_count = offices_list.count()

    paginator = Paginator(offices_list, results_per_page)
    page_number = request.GET.get('page')

    try:
        offices = paginator.get_page(page_number)
    except PageNotAnInteger:
        offices = paginator.get_page(1)
    except EmptyPage:
        offices = paginator.get_page(paginator.num_pages)

    context = {
        'offices': offices,
        'results_per_page': results_per_page,
        'filtered_offices': filtered_offices,  # القائمة المنسدلة
        'selected_office': selected_office,
        'filtered_offices_counts': filtered_offices.count(),
          'filtered_results_count': filtered_results_count,  # الوحدة المختارة
    }
    return render(request, 'hrhub/employee_office/office/main_offices.html', context)




@login_required
@permission_required('hrhub.can_add_office', raise_exception=True)
def add_office(request):
   
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            office = form.save(commit=False)
            office.created_by = request.user
            office.save()
            messages.success(request, "تم إضافة الوحدة الإدارية بنجاح.")
            return redirect('hrhub:main_offices')
    else:
        form = OfficeForm()
    return render(request, 'hrhub/employee_office/office/add_office.html', {'form': form})


@login_required
def office_detail(request, slug):
    # جلب العنوان الوظيفي المطلوب بناءً على slug
    office = get_object_or_404(Office, slug=slug)

    context = {
        'office': office
    }
    return render(request, 'hrhub/employee_office/office/office_detail.html', context)




@login_required
@permission_required('hrhub.can_update_office', raise_exception=True)
def update_office(request, slug):
   
    office = get_object_or_404(Office, slug=slug)
    if request.method == 'POST':
        form = OfficeForm(request.POST, instance=office)
        if form.is_valid():
            office.save()
            messages.success(request, "تم تعديل الوحدة الإدارية بنجاح.")
            return redirect('hrhub:main_offices')
    else:
        form = OfficeForm(instance=office)
    return render(request, 'hrhub/employee_office/office/update_office.html', {'form': form, 'office': office})



@login_required
@permission_required('hrhub.can_delete_office', raise_exception=True)
def delete_office(request, slug):
   
    office = get_object_or_404(Office, slug=slug)
    if not request.user.has_perm('hrhub.delete_office'):
        return HttpResponseForbidden("ليس لديك الصلاحية.")
    
    office.delete()
    messages.success(request, "تم حذف الوحدة الإدارية بنجاح.")
    return redirect('hrhub:main_offices')

import csv
from hrhub.forms.office_position import OfficeCSVUploadForm
from django.http import HttpResponse

@login_required
def download_offices_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="offices_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الاسم', 'الوحدة الإدارية العليا', 'ملاحظات']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        ['الإدارة العامة', '', 'الوحدة الإدارية الرئيسية'],
        ['قسم الموارد البشرية', 'الإدارة العامة', 'قسم يهتم بشؤون الموظفين'],
        ['قسم تكنولوجيا المعلومات', 'الإدارة العامة', 'قسم يهتم بتكنولوجيا المعلومات'],
       
    ]
    writer.writerows(example_rows)

    return response
import csv
import pandas as pd
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required



from django.contrib import messages
from django.shortcuts import render, redirect
import csv
from unidecode import unidecode
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required, permission_required

def clean_string(value):
    """تنظيف النص من المسافات الفارغة وأي رموز مخفية"""
    return value.strip() if value else None

@login_required
@permission_required('hrhub.can_add_office', raise_exception=True)
def upload_offices_csv(request):
    if request.method == 'POST':
        form = OfficeCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                # قراءة محتوى الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)
                
                # تنظيف أسماء الحقول من BOM إذا كان موجودًا
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')
                
                # قراءة جميع البيانات مع تنظيف القيم
                rows = []
                seen_offices = set()
                for row in reader:
                    name = clean_string(row.get('الاسم'))
                    parent_name = clean_string(row.get('الوحدة الإدارية العليا'))
                    comments = clean_string(row.get('ملاحظات'))
                    
                    if not name:
                        messages.error(request, f"اسم الوحدة الإدارية مفقود في السطر: {row}.")
                        continue
                    
                    row_key = (name, parent_name)
                    if row_key not in seen_offices:
                        rows.append({'name': name, 'parent_name': parent_name, 'comments': comments})
                        seen_offices.add(row_key)
                
                # إنشاء الإدارات العليا أولاً
                created_offices = {}
                for row in rows:
                    parent_name = row['parent_name']
                    if parent_name and parent_name not in created_offices:
                        parent = Office.objects.filter(name__iexact=parent_name).first()
                        if not parent:
                            parent, _ = Office.objects.get_or_create(
                                name=parent_name,
                                defaults={'created_by': request.user}
                            )
                        created_offices[parent_name] = parent
                
                # إنشاء الوحدات الإدارية وربطها بمكاتبها العليا
                for row in rows:
                    name = row['name']
                    parent_name = row['parent_name']
                    comments = row['comments']
                    parent = created_offices.get(parent_name) if parent_name else None
                    
                    Office.objects.update_or_create(
                        name=name,
                        defaults={
                            'parent': parent,
                            'comments': comments,
                            'created_by': request.user,
                        }
                    )
                
                messages.success(request, "تم تحميل البيانات وربط الوحدات الإدارية بنجاح!")
                return redirect('hrhub:main_offices')
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = OfficeCSVUploadForm()
    
    return render(request, 'hrhub/employee_office/office/upload_offices_csv.html', {'form': form})


#################################### Employee Office #############################
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from accounts.models import Employee

@login_required
def mainemployeeoffice(request):
    # التصفية الموجودة مسبقًا
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

    return render(request, 'hrhub/employee_office/mainemployeeoffice.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
    })




from hrhub.forms.office_position import EmployeeCSVUploadForm
from hrhub.models.office_position_models import EmployeeOffice


@login_required
@permission_required('hrhub.can_add_employee_office', raise_exception=True)
def upload_employees_csv(request):
    if request.method == 'POST':
        form = EmployeeCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # قراءة محتوى الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                for row in reader:
                    try:
                        # قراءة البيانات من كل صف باستخدام أسماء الأعمدة باللغة العربية
                        emp_id = row.get('الرقم الوظيفي', '').strip()
                        parent_office_name = row.get('الوحدة الإدارية العليا', '').strip()
                        office_name = row.get('الوحدة الإدارية', '').strip()

                        if not emp_id or not office_name:
                            messages.error(request, f"بيانات الموظف غير مكتملة في السطر: {row}.")
                            continue

                        # البحث عن الموظف في قاعدة البيانات
                        employee = Employee.objects.filter(username=emp_id).first()
                        if not employee:
                            messages.error(request, f"الموظف برقم {emp_id} غير موجود في النظام.")
                            continue

                        # البحث عن الوحدة الإدارية العليا وإنشاؤها إذا لم تكن موجودة
                        parent_office = None
                        if parent_office_name:
                            parent_office, _ = Office.objects.get_or_create(
                                name=parent_office_name,
                                defaults={'created_by': request.user}
                            )

                        # البحث عن الوحدة الإدارية وإنشاؤها إذا لم تكن موجودة
                        office, _ = Office.objects.get_or_create(
                            name=office_name,
                            defaults={'parent': parent_office, 'created_by': request.user}
                        )

                        # البحث عن BasicInfo للموظف
                        basic_info, _ = BasicInfo.objects.get_or_create(emp_id=employee)

                        # إنشاء أو تحديث سجل EmployeeOffice
                        EmployeeOffice.objects.update_or_create(
                            basic_info=basic_info,
                            office=office,
                            defaults={
                                'created_by': request.user
                            }
                        )

                    except Exception as e:
                        messages.error(request, f"حدث خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "تم تحميل بيانات الموظفين وربطهم بالوحدات الإدارية بنجاح!")
                return redirect('hrhub:mainemployeeoffice')  # استبدل `employee_offices` بالاسم المناسب
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = EmployeeCSVUploadForm()

    return render(request, 'hrhub/employee_office/upload_employees_csv.html', {'form': form})




@login_required
def download_employee_offices_csv_template(request):
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="offices_template.csv"'

    # إضافة UTF-8 BOM لضمان دعم اللغة العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين الأساسية بالعربية
    header = ['الرقم الوظيفي', 'الوحدة الإدارية العليا', 'الوحدة الإدارية']
    writer.writerow(header)

    # إضافة بيانات توضيحية كمثال
    example_rows = [
        
        ['7801201970', 'الادارة العامة', 'قسم تكنولوجيا المعلومات']
       
    ]
    writer.writerows(example_rows)

    return response

from django.http import JsonResponse

from hrhub.forms.office_position import EmployeeOfficeForm



@login_required
@permission_required('hrhub.can_add_employee_office', raise_exception=True)
def add_employee_office(request, slug):
    # الحصول على الموظف بناءً على `slug`
    employee = get_object_or_404(BasicInfo, slug=slug)

    if request.method == "POST":
        form = EmployeeOfficeForm(request.POST)
        if form.is_valid():
            # ربط العلاقة بالموظف
            employee_office = form.save(commit=False)
            employee_office.basic_info = employee
            employee_office.created_by = request.user  # تعيين المستخدم الذي أضاف العلاقة
            employee_office.save()
            messages.success(request, 'تمت إضافة الموظف إلى الدائرة بنجاح!')
            return redirect("hrhub:mainemployeeoffice")  # استبدلها بصفحة النجاح الخاصة بك

    else:
        form = EmployeeOfficeForm()

    return render(request, "hrhub/employee_office/employee_office_form.html", {"form": form, "employee": employee})

def load_emplloyee_offices(request):
    """عرض الوحدات الإدارية الفرعية عند اختيار وحدة رئيسية"""
    parent_id = request.GET.get("parent_office")
    offices = Office.objects.filter(parent_id=parent_id).order_by("name")
    return JsonResponse(list(offices.values("id", "name")), safe=False)



@login_required
def employee_offices_view(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # جلب جميع علاقات الموظف بالدوائر
    employee_offices = EmployeeOffice.objects.filter(basic_info=employee)

    return render(request, 'hrhub/employee_office/employee_offices.html', {
        'employee': employee, 
        'employee_offices': employee_offices
    })


@login_required
def employee_offices_viewemployee(request, slug):
    employee = get_object_or_404(BasicInfo, slug=slug)
    
    # جلب جميع علاقات الموظف بالدوائر
    employee_offices = EmployeeOffice.objects.filter(basic_info=employee)

    return render(request, 'hrhub/employee_office/employee_offices_viewemployee.html', {
        'employee': employee, 
        'employee_offices': employee_offices
    })


# from hrhub.forms.office_position import EmployeeUpdateOfficeForm

@login_required
@permission_required('hrhub.can_update_employee_office', raise_exception=True)
def update_employee_office(request, slug):
    employee_office = get_object_or_404(EmployeeOffice, slug=slug)

    if request.method == 'POST':
        form = EmployeeOfficeForm(request.POST, instance=employee_office)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث دائرة الموظف بنجاح.")
            return redirect('hrhub:employee_offices_view', slug=employee_office.basic_info.slug)  # إعادة التوجيه بعد التحديث
    else:
        form = EmployeeOfficeForm(instance=employee_office)

    return render(request, 'hrhub/employee_office/employee_office_update_form.html', 
                  {'form': form, 'employee_office': employee_office})



@login_required
@permission_required('hrhub.can_delete_employee_office', raise_exception=True)
def delete_employee_office(request, slug):
    # جلب علاقة الموظف بالدائرة باستخدام الـ slug
    employee_office = get_object_or_404(EmployeeOffice, slug=slug)
    
    # حذف علاقة الموظف بالدائرة
    employee_office.delete()
    
    # رسالة تأكيد الحذف
    messages.success(request, "تم حذف علاقة الموظف بالدائرة بنجاح.")
    
    # إعادة التوجيه إلى صفحة الموظف بعد الحذف
    return redirect('hrhub:employee_offices_view', slug=employee_office.basic_info.slug)