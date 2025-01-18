from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from accounts.models import Employee
from personalinfo.models import BasicInfo
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from accounts.models import Employee
from django.db.models import Q

from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render


from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseForbidden


from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseForbidden

from hrhub.models.hr_utilities_models import PlaceOfEmployment, DutyAssignmentOrder

from django.shortcuts import render, get_object_or_404, redirect
from hrhub.forms.placement import PlacementForm

from django.contrib import messages
from django.db.models import Exists, OuterRef

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied



@login_required
def main_placement(request):

    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    placement_type_query = request.GET.get('placement_type', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    place_of_placement_query = request.GET.get('place_of_placement', '')
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
    if placement_type_query:
        query &= Q(basic_info__employee_placement__placement_type=placement_type_query)

    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)
    if place_of_placement_query:
        query &= Q(basic_info__employee_placement__place_of_placement__id=place_of_placement_query)

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    places = PlaceOfEmployment.objects.all()
    employees = Employee.objects.filter(query).annotate(
        has_placement=Exists(
            Placement.objects.filter(basic_info__emp_id=OuterRef('id'))
        )
    )
    

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

    return render(request, 'hrhub/placement/main_placement.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'places': places,  
    })



@login_required
@permission_required('hrhub.can_add_placement', raise_exception=True)
def add_placement(request, slug):
    # الحصول على الموظف بناءً على السلاUG
    employee = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = PlacementForm(request.POST, request.FILES)
        if form.is_valid():
            # ربط التنسيب بالموظف الحالي
            placement = form.save(commit=False)
            placement.basic_info = employee
            placement.created_by = request.user  # تعيين المستخدم الذي أضاف التنسيب
            placement.save()
            messages.success(request, 'تم إضافة التنسيب بنجاح!')
            return redirect('hrhub:main_placement')  # إعادة التوجيه إلى صفحة التفاصيل

    else:
        form = PlacementForm()

    return render(request, 'hrhub/placement/add_placement.html', {
        'form': form,
        'employee': employee,
    })

@login_required
def all_placement_detailemployee(request, slug):
    # استخدام BasicInfo للبحث عن الموظف
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع خيارات نوع التنسيب
    PLACEMENT_CHOICES = Placement.PLACEMENT_CHOICES

    # استلام نوع التنسيب المحدد من طلب GET
    selected_placement_type = request.GET.get('placement_type', '')

    # تصفية التنسيب بناءً على النوع المحدد
    placements = Placement.objects.filter(basic_info=basic_info)
    if selected_placement_type:
        placements = placements.filter(placement_type=selected_placement_type)

    # حساب عدد سجلات التنسيب بعد التصفية
    placements_count = placements.count()

    return render(request, 'hrhub/placement/all_placement_detailemployee.html', {
        'employee': basic_info,
        'placements': placements,
        'PLACEMENT_CHOICES': PLACEMENT_CHOICES,
        'selected_placement_type': selected_placement_type,
        'placements_count': placements_count,  # عدد التنسيبات لعرضه في القائمة الجانبية
    })




@login_required
def all_placement_detail(request, slug):
    # استخدام BasicInfo للبحث عن الموظف
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    placements = Placement.objects.filter(basic_info=basic_info)

    return render(request, 'hrhub/placement/all_placement_detail.html', {'employee': basic_info, 'placements': placements})

from django.shortcuts import render, get_object_or_404
from hrhub.models.placement_models import Placement

@login_required
def placement_detail(request, slug):
    # الحصول على تفاصيل التنسيب باستخدام slug
    placement = get_object_or_404(Placement, slug=slug)
    
    # تمرير التفاصيل إلى القالب
    return render(request, 'hrhub/placement/placement_detail.html', {'placement': placement})




@login_required
@permission_required('hrhub.can_update_placement', raise_exception=True)
def update_placement(request, placement_slug):
    # جلب التنسيب باستخدام السلاUG فقط
    placement = get_object_or_404(Placement, slug=placement_slug)

    if request.method == 'POST':
        form = PlacementForm(request.POST, request.FILES, instance=placement)
        if form.is_valid():
            # حفظ التحديثات
            form.save()
            messages.success(request, 'تم تحديث التنسيب بنجاح!')
            return redirect('hrhub:main_placement')  # إعادة التوجيه إلى صفحة التنسيب بعد التحديث
    else:
        form = PlacementForm(instance=placement)

    return render(request, 'hrhub/placement/update_placement.html', {
        'form': form,
        'placement': placement
    })


@login_required
@permission_required('hrhub.can_delete_placement', raise_exception=True)
def delete_placement(request, placement_slug):
   
    
   
    placement = get_object_or_404(Placement, slug=placement_slug)
    
    # حذف التنسيب
    placement.delete()
    
    # عرض رسالة نجاح
    messages.success(request, "تم حذف التنسيب بنجاح.")
    
    # إعادة التوجيه إلى الصفحة الرئيسية للتنسيبات
    return redirect('hrhub:main_placement')







import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode

from hrhub.forms.placement import PlacementCSVUploadForm

# ✅ دالة لتحويل صيغ التاريخ المختلفة إلى YYYY-MM-DD
def parse_date(date_string):
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None




import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.text import slugify
from unidecode import unidecode

# ✅ دالة لتحويل صيغ التاريخ المختلفة إلى YYYY-MM-DD
def parse_date(date_string):
    if not date_string:
        return None
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    return None

@login_required
@permission_required('hrhub.can_add_placement', raise_exception=True)
def upload_placement_csv(request):
    if request.method == 'POST':
        form = PlacementCSVUploadForm(request.POST, request.FILES)
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
                        placement_type = row.get('نوع التنسيب', '').strip()
                        place_of_placement_name = row.get('مكان التنسيب', '').strip()
                        order_of_placement_name = row.get('نوع أمر التنسيب', '').strip()
                        order_number = row.get('رقم الأمر الصادر', '').strip()
                        start_date_str = row.get('تاريخ بداية التنسيب', '').strip()
                        end_date_str = row.get('تاريخ نهاية التنسيب', '').strip()

                        # ✅ تحويل التواريخ إلى تنسيق صحيح
                        start_date = parse_date(start_date_str)
                        end_date = parse_date(end_date_str)

                        # ✅ التحقق من البيانات الأساسية
                        if not emp_id or not placement_type or not start_date:
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

                        # ✅ البحث عن مكان التنسيب أو إنشاؤه
                        place_of_placement = None
                        if place_of_placement_name:
                            place_of_placement, _ = PlaceOfEmployment.objects.get_or_create(
                                name_in_arabic=place_of_placement_name
                            )

                        # ✅ البحث عن نوع أمر التنسيب أو إنشاؤه
                        order_of_placement = None
                        if order_of_placement_name:
                            order_of_placement, _ = DutyAssignmentOrder.objects.get_or_create(
                                name_in_arabic=order_of_placement_name
                            )

                        # ✅ إنشاء سجل Placement
                        placement = Placement.objects.create(
                            basic_info=basic_info,
                            placement_type=placement_type,
                            place_of_placement=place_of_placement,
                            order_of_placement=order_of_placement,
                            name=order_number,
                            start_date=start_date,
                            end_date=end_date
                        )

                    except Exception as e:
                        messages.error(request, f"❌ خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "✅ تم تحميل بيانات التنسيب بنجاح!")
                return redirect('hrhub:main_placement')  # استبدل `your_app` باسم تطبيقك

            except Exception as e:
                messages.error(request, f"❌ حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "❌ يرجى التأكد من صحة البيانات.")
    else:
        form = PlacementCSVUploadForm()

    return render(request, 'hrhub/placement/upload_placement_csv.html', {'form': form})