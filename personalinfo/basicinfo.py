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
from .models import BasicInfo, Employee
from locations.models import Governorate
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BasicInfo
import csv
from django.db.models import Q
from django.shortcuts import render
from .models import Employee
from django.utils.encoding import smart_str
from django.shortcuts import render
from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from hrhub.models.office_position_models import Office

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@login_required
def mainbasicinfo(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_phone = request.GET.get('has_phone', '')
    office_query = request.GET.get('office', '')
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
    if has_basicinfo:
        if has_basicinfo.lower() == 'yes':
            query &= Q(basic_info__isnull=False)  # شرط AND
        elif has_basicinfo.lower() == 'no':
            query &= Q(basic_info__isnull=True)  # شرط AND

    if gender_query:  # إضافة شرط البحث عن الجنس
        query &= Q(basic_info__gender=gender_query)
    
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)

    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    

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
    root_offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__parent__isnull=True))

    return render(request, 'personalinfo/basicinfo/mainbasicinfo.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
        'offices': root_offices,
    })



######################## Add basic info ####################

from .forms import BasicInfoForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
@permission_required('personalinfo.can_add_employee_basic_info', raise_exception=True)
def addbasicinfo(request, slug):
   
    employee = get_object_or_404(Employee, slug=slug)

    if hasattr(employee, 'basic_info'):
        return redirect('personalinfo:mainbasicinfo')

    if request.method == 'POST':
        form = BasicInfoForm(request.POST, request.FILES, emp_id=employee, created_by=request.user)
        if form.is_valid():
            basic_info = form.save(commit=False)
            basic_info.created_by = request.user
            basic_info.is_approved = True
            basic_info.save()
            messages.success(request, 'تم حفظ المعلومات الأساسية بنجاح.')
            return redirect('personalinfo:mainbasicinfo')
    else:
        form = BasicInfoForm(emp_id=employee, created_by=request.user)

    return render(request, 'personalinfo/basicinfo/addbasicinfo.html', {'form': form, 'employee': employee,
                                                                        'created_by': request.user})

@login_required
def basicinfodetail(request, slug):
    # الحصول على الموظف بناءً على السلاج
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    # تمرير بيانات الموظف إلى القالب
    return render(request, 'personalinfo/basicinfo/basicinfodetail.html', {'basic_info': basic_info})

@login_required
@permission_required('personalinfo.can_update_employee_basic_info', raise_exception=True)
def updatebasicinfo(request, slug):
    basic_info_instance = get_object_or_404(BasicInfo, slug=slug)

    basic_info = basic_info_instance

    # # التحقق من الصلاحيات
    # if not request.user.has_perm('app_name.can_update_firstname'):
    #     return HttpResponseForbidden("ليس لديك الصلاحية لتحديث البيانات.")

    if request.method == 'POST':
        form = BasicInfoForm(request.POST, request.FILES, instance=basic_info_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث البيانات بنجاح.")
            return redirect('personalinfo:basicinfodetail', slug=slug)
    else:
        form = BasicInfoForm(instance=basic_info_instance)
    
    return render(request, 'personalinfo/basicinfo/updatebasicinfo.html', {'form': form,
                                                                           'basic_info': basic_info,
                                                                           'created_by': request.user})

from django.db import IntegrityError

@login_required
@permission_required('personalinfo.can_delete_employee_basic_info', raise_exception=True)
def deletedetailsbasicinfo(request, slug):
    # التحقق من صلاحية المستخدم
   
    
    # محاولة الحصول على السجل
    basicinfo = get_object_or_404(BasicInfo, slug=slug)
    
    try:
        # محاولة حذف السجل
        basicinfo.delete()
        messages.success(request, "تم حذف هذه البيانات بنجاح.")
        return redirect('personalinfo:mainbasicinfo')  # إعادة التوجيه إلى الصفحة الرئيسية بعد الحذف
    except IntegrityError:
        # في حالة وجود مشكلة في الحذف بسبب قيود FOREIGN KEY
        messages.error(request, "لا يمكن حذف هذه البيانات لأنها مرتبطة بسجلات أخرى.")
        
        # إعادة التوجيه إلى صفحة عرض المعلومات الأساسية للسجل المرتبط
        return redirect('personalinfo:employee_detail', slug=basicinfo.slug)






@login_required
def download_sample_basic_info_csv(request):
    # إعداد الاستجابة ليتم تحميلها كملف CSV مع الترميز المناسب لدعم اللغة العربية
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="basic_info_sample.csv"'

    # إعداد كاتب CSV مع الترميز المناسب
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة عناوين الأعمدة (باللغة العربية) بعد إزالة الحقول التلقائية
    header = [
        'المعرف', 'الاسم الأول', 'الاسم الثاني', 'الاسم الثالث',
        'الاسم الرابع', 'اللقب', 'اسم الأم', 'رقم الهاتف',
        'البريد الإلكتروني', 'تاريخ الميلاد', 'مكان الميلاد',
        'الجنس', 'الملف الشخصي'
    ]
    writer.writerow(header)

    # كتابة صفوف البيانات (عينات بيانات ثابتة) بعد إزالة الحقول التلقائية
    sample_rows = [
        ['1', 'أحمد', 'محمد', 'علي', 'حسين', 'العراقي', 'فاطمة', '07701234567',
         'ahmed@example.com', '1992-04-20', 'بغداد', 'ذكر',  ''],

        
    ]
    writer.writerows(sample_rows)

    return response


from .forms import BasicInfoCSVUploadForm
from django.utils.text import slugify
from unidecode import unidecode


@login_required
@permission_required('personalinfo.can_add_employee_basic_info', raise_exception=True)
def upload_basic_info_csv(request):
    if not request.user.has_perm('personalinfo.add_basicinfo'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    if request.method == 'POST':
        form = BasicInfoCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # قراءة محتوى الملف
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)
            
            next(reader)  # تخطي العنوان
            for row in reader:
                try:
                    # التحقق من صحة السطر
                    if len(row) < 12:
                        messages.error(request, f"السطر {row} يحتوي على بيانات ناقصة.")
                        continue
                    
                    # استخراج الرقم الوظيفي (username)
                    emp_username = row[0]
                    
                    # البحث عن الموظف باستخدام الرقم الوظيفي (username)
                    try:
                        emp = Employee.objects.get(username=emp_username)
                    except Employee.DoesNotExist:
                        messages.error(request, f"الموظف الذي لديه الرقم الوظيفي {emp_username} غير موجود في قاعدة البيانات.")
                        continue

                    # استخراج باقي البيانات مع التحقق من الحقول الفارغة
                    firstname = row[1].strip() if row[1].strip() else None
                    secondname = row[2].strip() if row[2].strip() else None
                    thirdname = row[3].strip() if row[3].strip() else None
                    fourthname = row[4].strip() if row[4].strip() else None
                    surname = row[5].strip() if row[5].strip() else None
                    mothername = row[6].strip() if row[6].strip() else None
                    phone_number = row[7].strip() if row[7].strip() else None
                    email = row[8].strip() if row[8].strip() else None
                    
                    # تحويل تاريخ الميلاد
                    date_of_birth = row[9]
                    if date_of_birth.strip():
                        try:
                            date_of_birth = datetime.strptime(date_of_birth.strip(), '%d/%m/%Y').date()
                        except ValueError:
                            messages.error(request, f"تاريخ الميلاد {date_of_birth} غير صالح. يجب أن يكون بالتنسيق DD/MM/YYYY.")
                            continue
                    else:
                        date_of_birth = None

                    # استخراج مكان الميلاد
                    place_of_birth = Governorate.objects.filter(name_arabic=row[10].strip()).first() if row[10].strip() else None
                    if not place_of_birth and row[10].strip():
                        messages.error(request, f"المحافظة {row[10]} غير موجودة في قاعدة البيانات.")
                        continue
                    
                    gender = row[11].strip() if row[11].strip() else None
                    
                    
                    # تعيين المستخدم الذي قام بالتحميل
                    created_by = request.user if isinstance(request.user, Employee) else None
                    
                    # التحقق من وجود البريد الإلكتروني مسبقًا إذا كان غير فارغ
                    if email:
                        existing_email = BasicInfo.objects.filter(email=email).exclude(emp_id=emp).exists()
                        if existing_email:
                            messages.error(request, f"البريد الإلكتروني {email} مرتبط بالفعل بسجل آخر.")
                            continue
                    
                    # إنشاء أو تحديث BasicInfo
                    # توليد سلاج فريد
                    base_slug = slugify(unidecode(f"{firstname or ''} {secondname or ''} {thirdname or ''} {surname or ''}".strip()))
                    unique_slug = base_slug
                    count = 1
                    while BasicInfo.objects.filter(slug=unique_slug).exists():
                        unique_slug = f"{base_slug}-{count}"
                        count += 1
                    
                    # إنشاء أو تحديث السجل
                    basic_info, created = BasicInfo.objects.update_or_create(
                        emp_id=emp,
                        defaults={
                            'firstname': firstname,
                            'secondname': secondname,
                            'thirdname': thirdname,
                            'fourthname': fourthname,
                            'surname': surname,
                            'mothername': mothername,
                            'phone_number': phone_number,
                            'email': email,
                            'date_of_birth': date_of_birth,
                            'place_of_birth': place_of_birth,
                            'gender': gender,
                            'slug': unique_slug,
                            'created_by': created_by,
                            'is_approved': True
                        }
                    )
                except Exception as e:
                    messages.error(request, f"حدث خطأ عند إدخال السجل: {row}. الخطأ: {e}")
                    continue

            messages.success(request, "تم تحميل البيانات بنجاح!")
            return redirect('personalinfo:mainbasicinfo')
    else:
        form = BasicInfoCSVUploadForm()
    
    return render(request, 'personalinfo/basicinfo/basicinfo_upload_csv.html', {'form': form})



@login_required
def export_basic_info_to_csv(request):
    # استلام القيم من استعلام البحث
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    office_query = request.GET.get('office', '')

    # بناء استعلام Q مع شروط مركبة
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
        if has_basicinfo.lower() == 'yes':
            query &= Q(basic_info__isnull=False)
        elif has_basicinfo.lower() == 'no':
            query &= Q(basic_info__isnull=True)
    if gender_query:
        query &= Q(basic_info__gender=gender_query)
    if has_phone:
        if has_phone.lower() == 'yes':
            query &= Q(basic_info__phone_number__isnull=False)
        elif has_phone.lower() == 'no':
            query &= Q(basic_info__phone_number__isnull=True)
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    # تطبيق الاستعلام على الموظفين
    employees = Employee.objects.filter(query)

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="filtered_basic_info.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    
    # كتابة الرأس
    writer.writerow([
        smart_str('الرقم الوظيفي', encoding='utf-8', errors='ignore'),
        smart_str('الاسم الكامل', encoding='utf-8', errors='ignore'),
        smart_str('رقم الهاتف', encoding='utf-8', errors='ignore'),
        smart_str('البريد الإلكتروني', encoding='utf-8', errors='ignore'),
        smart_str('الجنس', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الميلاد', encoding='utf-8', errors='ignore'),
        smart_str('الدائرة', encoding='utf-8', errors='ignore'),
    ])

    # كتابة البيانات
    for employee in employees:
        basic_info = getattr(employee, 'basic_info', None)
        full_name = basic_info.get_full_name() if basic_info else 'غير متوفرة'
        phone_number = basic_info.phone_number if basic_info else 'غير متوفرة'
        email = basic_info.email if basic_info else 'غير متوفرة'
        gender = basic_info.get_gender_display() if basic_info and basic_info.gender else 'غير متوفرة'
        date_of_birth = basic_info.date_of_birth.strftime('%d/%m/%Y') if basic_info and basic_info.date_of_birth else 'غير متوفرة'
        office = employee.get_office_display() if hasattr(employee, 'get_office_display') else 'غير متوفرة'

        writer.writerow([
            smart_str(employee.username, encoding='utf-8', errors='ignore'),
            smart_str(full_name, encoding='utf-8', errors='ignore'),
            smart_str(phone_number, encoding='utf-8', errors='ignore'),
            smart_str(email, encoding='utf-8', errors='ignore'),
            smart_str(gender, encoding='utf-8', errors='ignore'),
            smart_str(date_of_birth, encoding='utf-8', errors='ignore'),
            smart_str(office, encoding='utf-8', errors='ignore'),
        ])

    return response




######################################### Update

########################## Update Basic Info ##########################


# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import BasicInfo
from .forms import UpdateFirstNameForm
from django.core.exceptions import PermissionDenied


@login_required
@permission_required('personalinfo.can_update_firstname', raise_exception=True)
def update_firstname(request, slug):
    
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateFirstNameForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث الاسم الأول بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه باستخدام slug
    else:
        form = UpdateFirstNameForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_firstname.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdateSecondNameForm


@login_required
@permission_required('personalinfo.can_update_secondname', raise_exception=True)
def update_secondname(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateSecondNameForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث الاسم الثاني بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateSecondNameForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_secondname.html', {'form': form, 'basic_info': basic_info})



# views.py
from .forms import UpdateThirdNameForm

@login_required
@permission_required('personalinfo.can_update_thirdname', raise_exception=True)
def update_thirdname(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateThirdNameForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث الاسم الثالث بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateThirdNameForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_thirdname.html', {'form': form, 'basic_info': basic_info})



from .forms import UpdateFourthNameForm


@login_required
@permission_required('personalinfo.can_update_fourthname', raise_exception=True)
def update_fourthname(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateFourthNameForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث الاسم الرابع بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateFourthNameForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_fourthname.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdateSurnameForm


@login_required
@permission_required('personalinfo.can_update_surname', raise_exception=True)
def update_surname(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateSurnameForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث اللقب بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateSurnameForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_surname.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdateMotherNameForm

@login_required
@permission_required('personalinfo.can_update_mothername', raise_exception=True)
def update_mother_name(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateMotherNameForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث اسم الأم بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateMotherNameForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_mother_name.html', {'form': form, 'basic_info': basic_info})

from .forms import UpdatePhoneNumberForm

@login_required
@permission_required('personalinfo.can_update_phonenumber', raise_exception=True)
def update_phone_number(request, slug):
  
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdatePhoneNumberForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث رقم الهاتف بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdatePhoneNumberForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_phone_number.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdateEmailForm

@login_required
@permission_required('personalinfo.can_update_email', raise_exception=True)
def update_email(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateEmailForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث البريد الإلكتروني بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateEmailForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_email.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdateDateOfBirthForm
from django.contrib import messages

@login_required
@permission_required('personalinfo.can_update_date_of_birth', raise_exception=True)
def update_date_of_birth(request, slug):
    
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateDateOfBirthForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث تاريخ الميلاد بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث
    else:
        form = UpdateDateOfBirthForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_date_of_birth.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdatePlaceOfBirthForm

@login_required
@permission_required('personalinfo.can_update_place_of_birth', raise_exception=True)
def update_place_of_birth(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdatePlaceOfBirthForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث مكان الميلاد بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث (عدل الـ URL هنا حسب الحاجة)
    else:
        form = UpdatePlaceOfBirthForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_place_of_birth.html', {'form': form, 'basic_info': basic_info})

from .forms import UpdateGenderForm

@login_required
@permission_required('personalinfo.can_update_gender', raise_exception=True)
def update_gender(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateGenderForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث الجنس بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث (عدل الـ URL حسب الحاجة)
    else:
        form = UpdateGenderForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_gender.html', {'form': form, 'basic_info': basic_info})

from .forms import UpdateBioForm
from django.contrib import messages

@login_required
@permission_required('personalinfo.can_update_bio', raise_exception=True)
def update_bio(request, slug):
   
    basic_info = get_object_or_404(BasicInfo, slug=slug)
    
    if request.method == 'POST':
        form = UpdateBioForm(request.POST, instance=basic_info)
        if form.is_valid():
            form.save()  # حفظ التحديث
            messages.success(request, 'تم تحديث السيرة الذاتية بنجاح!')
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث (عدل الـ URL حسب الحاجة)
    else:
        form = UpdateBioForm(instance=basic_info)
    
    return render(request, 'personalinfo/basicinfo/updates/update_bio.html', {'form': form, 'basic_info': basic_info})


from .forms import UpdateAvatarForm
from django.contrib import messages
from personalinfo.models import BasicInfoChangeLog

@login_required
@permission_required('personalinfo.can_update_avatar', raise_exception=True)
def update_avatar(request, slug):
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = UpdateAvatarForm(request.POST, request.FILES, instance=basic_info)
        if form.is_valid():
            old_avatar = basic_info.avatar  # حفظ الصورة القديمة
            new_avatar = request.FILES.get('avatar')  # الصورة الجديدة

            # تحديث الصورة الشخصية
            form.save()

            # تسجيل التغيير في سجل التعديلات
            BasicInfoChangeLog.objects.create(
                basic_info=basic_info,
                action="update",
                field_name="avatar",
                old_value=str(old_avatar) if old_avatar else None,
                new_value=str(new_avatar) if new_avatar else None,
                user=request.user,  # الشخص الذي قام بالتحديث
            )

            messages.success(request, 'تم تحديث الصورة بنجاح!')
            return redirect('accounts:view_profile')

    else:
        form = UpdateAvatarForm(instance=basic_info)

    return render(request, 'personalinfo/basicinfo/updates/update_avatar.html', {'form': form, 'basic_info': basic_info})