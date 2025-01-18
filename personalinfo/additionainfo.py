from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.utils.dateparse import parse_date
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from hrhub.models.office_position_models import Office
import csv
from datetime import datetime
from unidecode import unidecode

from .models import BasicInfo, AdditionalInfo, Religion, Nationalism
from accounts.models import Employee
from locations.models import Governorate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied





@login_required
def main_additionainfo(request):

    religions = Religion.objects.all()
    nationalisms = Nationalism.objects.all()  # جلب قائمة القوميات

    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')  # إضافة الحصول على قيمة الجنس
    has_additionalinfo = request.GET.get('has_additionalinfo', '')
    office_query = request.GET.get('office', '')
    religion_query = request.GET.get('religion', '')
    nationalism_query = request.GET.get('nationalism', '')
    blood_type_query = request.GET.get('blood_type', '')  
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
    
    if has_additionalinfo:
        if has_additionalinfo.lower() == 'yes':
            query &= Q(basic_info__additional_info__isnull=False)  # شرط AND
        elif has_additionalinfo.lower() == 'no':
            query &= Q(basic_info__additional_info__isnull=True)  # شرط AND
    if religion_query:
        query &= Q(basic_info__additional_info__religion__id=religion_query)
    
    if nationalism_query:  # إضافة شرط البحث عن القومية
        query &= Q(basic_info__additional_info__nationalism__id=nationalism_query)
    
    if blood_type_query:  # إضافة شرط البحث عن فصيلة الدم
        query &= Q(basic_info__additional_info__blood_type=blood_type_query)
    
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass
    

    # تطبيق الاستعلام على نموذج الموظفين
    employees = Employee.objects.filter(query)
    root_offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__parent__isnull=True))

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

    return render(request, 'personalinfo/additionainfo/main_additionainfo.html', {
        'employees': page_obj,
        'employee_count': employee_count,
        'results_per_page': results_per_page,
         'religions': religions, 
         'nationalisms': nationalisms,
           'offices': root_offices,  # تمرير القوميات  
    })



from .forms import AdditionalinfoForm



@login_required
@permission_required('personalinfo.can_add_employee_additional_info', raise_exception=True)
def add_additional_info(request, slug):
  
    basic_info = get_object_or_404(BasicInfo, slug=slug)

    # تحقق إذا كانت هناك معلومات إضافية مرتبطة بالفعل
    if hasattr(basic_info, 'additional_info'):  # التحقق من العلاقة OneToOne
        return HttpResponseRedirect(reverse('personalinfo:additional_info_detail', kwargs={'slug': slug}))

    # معالجة الطلب POST
    if request.method == "POST":
        form = AdditionalinfoForm(request.POST, request.FILES)
        if form.is_valid():
            additional_info = form.save(commit=False)
            additional_info.basic_info = basic_info  # ربط BasicInfo
            additional_info.created_by = request.user
            additional_info.is_approved = True # ربط المستخدم الحالي
            additional_info.save()
            messages.success(request, "تم إضافة المعلومات الإضافية بنجاح.")
            return HttpResponseRedirect(reverse('personalinfo:main_additionainfo'))
        else:
            messages.error(request, "حدث خطأ أثناء إدخال البيانات. الرجاء التحقق من الحقول.")
    else:
        form = AdditionalinfoForm()

    # عرض النموذج
    return render(request, 'personalinfo/additionainfo/add_additional_info.html', {
        'form': form,
        'basic_info': basic_info,
    })






@login_required
def additional_info_detail(request, slug):
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)
    return render(request, 'personalinfo/additionainfo/additional_info_detail.html', {'additional_info': additional_info})




@login_required
@permission_required('personalinfo.can_update_employee_additional_info', raise_exception=True)
def update_additional_info(request, slug):
    # الحصول على الكائن باستخدام slug بدلاً من pk
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)
    
    if request.method == 'POST':
        form = AdditionalinfoForm(request.POST, request.FILES, instance=additional_info)
        if form.is_valid():
            form.save()
            return redirect('personalinfo:additional_info_detail', slug=slug)  # بعد التحديث، يمكنك إعادة التوجيه إلى صفحة النجاح
    else:
        form = AdditionalinfoForm(instance=additional_info)
    
    return render(request, 'personalinfo/additionainfo/update_additional_info.html', {'form': form, 'additional_info': additional_info})



@login_required
@permission_required('personalinfo.can_delete_employee_additional_info', raise_exception=True)
def delete_additional_info(request, slug):
    # التحقق من الصلاحيات: تأكد من أن المستخدم لديه صلاحية الحذف
    if not request.user.has_perm('personalinfo.delete_additionalinfo'):
        return HttpResponseForbidden("ليس لديك الصلاحية لحذف هذه المعلومات.")
    
    # الحصول على الكائن باستخدام slug
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)

    # حذف الكائن
    additional_info.delete()

    # إعادة التوجيه بعد الحذف
    return redirect('personalinfo:main_additionainfo')


from .forms import AdditionalInfoCSVUploadForm

@login_required
@permission_required('personalinfo.can_add_employee_additional_info', raise_exception=True)
def upload_additional_info_csv(request):
    if request.method == 'POST':
        form = AdditionalInfoCSVUploadForm(request.POST, request.FILES)
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
                        blood_type = row[1].strip() if row[1].strip() else None
                        religion_name = row[2].strip() if row[2].strip() else None
                        nationalism_name = row[3].strip() if row[3].strip() else None
                        marital_status = row[4].strip() if row[4].strip() else None
                        governorate_of_residence_name = row[5].strip() if row[5].strip() else None
                        address = row[6].strip() if row[6].strip() else None
                        emergency_contact_name = row[7].strip() if row[7].strip() else None
                        emergency_contact_number = row[8].strip() if row[8].strip() else None

                        # جلب الموظف وBasicInfo المرتبط به
                        try:
                            emp = Employee.objects.get(username=emp_username)
                            basic_info = emp.basic_info
                        except (Employee.DoesNotExist, BasicInfo.DoesNotExist):
                            messages.error(request, f"الموظف برقم وظيفي {emp_username} غير موجود أو لا يحتوي على BasicInfo.")
                            continue

                        # جلب الكيانات المرتبطة
                        religion = Religion.objects.filter(name_in_arabic=religion_name).first() if religion_name else None
                        nationalism = Nationalism.objects.filter(name_in_arabic=nationalism_name).first() if nationalism_name else None
                        governorate_of_residence = Governorate.objects.filter(name_arabic=governorate_of_residence_name).first() if governorate_of_residence_name else None

                        # التحقق من رقم الطوارئ
                        if emergency_contact_number and not emergency_contact_number.isdigit():
                            messages.error(request, f"رقم الطوارئ {emergency_contact_number} في السطر {row} غير صحيح.")
                            continue

                        # إنشاء أو تحديث AdditionalInfo
                        additional_info, created = AdditionalInfo.objects.update_or_create(
                            basic_info=basic_info,
                            defaults={
                                'blood_type': blood_type,
                                'religion': religion,
                                'nationalism': nationalism,
                                'marital_status': marital_status,
                                'governorate_of_residence': governorate_of_residence,
                                'address': address,
                                'emergency_contact_name': emergency_contact_name,
                                'emergency_contact_number': emergency_contact_number,
                                'created_by': request.user if isinstance(request.user, Employee) else None,
                                'is_approved': True,
                            }
                        )
                    except Exception as e:
                        messages.error(request, f"خطأ أثناء معالجة السطر {row}: {str(e)}")
                        continue

                # رسالة نجاح
                messages.success(request, "تم تحميل البيانات بنجاح!")
                return redirect('personalinfo:main_additionainfo')
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء قراءة الملف: {str(e)}")
    else:
        form = AdditionalInfoCSVUploadForm()

    return render(request, 'personalinfo/additionainfo/additionalinfo_upload_csv.html', {'form': form})


@login_required
def download_sample_additional_info_csv(request):
    # إعداد الاستجابة ليتم تحميلها كملف CSV مع الترميز المناسب لدعم اللغة العربية
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="additional_info_sample.csv"'

    # إعداد كاتب CSV مع الترميز المناسب
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة عناوين الأعمدة باللغة العربية
    header = [
        'المعرف', 'فصيلة الدم', 'الديانة', 'القومية', 'الحالة الاجتماعية',
        'المحافظة السكنية', 'العنوان', 'اسم الشخص للطوارئ', 'رقم الطوارئ',
    ]
    writer.writerow(header)

    # إضافة المعرف وفصيلة الدم مع ترك باقي الحقول فارغة
    sample_rows = [
        ['7801201970', '', '', '', '', '','', '', ''],
    ]
    writer.writerows(sample_rows)

    return response



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str


import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str



@login_required
def export_additional_info_to_csv(request):
    # استلام القيم من استعلام البحث
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_additionalinfo = request.GET.get('has_additionalinfo', '')
    religion_query = request.GET.get('religion', '')
    nationalism_query = request.GET.get('nationalism', '')
    blood_type_query = request.GET.get('blood_type', '')
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
    if has_additionalinfo:
        if has_additionalinfo.lower() == 'yes':
            query &= Q(basic_info__additional_info__isnull=False)
        elif has_additionalinfo.lower() == 'no':
            query &= Q(basic_info__additional_info__isnull=True)
    if religion_query:
        query &= Q(basic_info__additional_info__religion__id=religion_query)
    if nationalism_query:
        query &= Q(basic_info__additional_info__nationalism__id=nationalism_query)
    if blood_type_query:
        query &= Q(basic_info__additional_info__blood_type=blood_type_query)
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    # تطبيق الاستعلام
    employees = Employee.objects.filter(query)

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="additional_info.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    # كتابة الرأس
    writer.writerow([
        smart_str('الرقم الوظيفي', encoding='utf-8'),
        smart_str('الاسم الكامل', encoding='utf-8'),
        smart_str('الجنس', encoding='utf-8'),
        smart_str('القومية', encoding='utf-8'),
        smart_str('الديانة', encoding='utf-8'),
        smart_str('فصيلة الدم', encoding='utf-8'),
        smart_str('الحالة الاجتماعية', encoding='utf-8'),
        smart_str('المحافظة', encoding='utf-8'),
        smart_str('العنوان', encoding='utf-8'),
        smart_str('اسم الطوارئ', encoding='utf-8'),
        smart_str('رقم الطوارئ', encoding='utf-8'),
    ])

    # كتابة البيانات
    for employee in employees:
        basic_info = getattr(employee, 'basic_info', None)
        if basic_info:
            full_name = basic_info.get_full_name()
            gender = basic_info.get_gender_display() if basic_info.gender else 'غير متوفر'
        else:
            full_name = 'غير متوفر'
            gender = 'غير متوفر'

        additional_info = getattr(basic_info, 'additional_info', None) if basic_info else None
        nationalism = additional_info.nationalism.name_in_arabic if additional_info and additional_info.nationalism else 'غير متوفر'
        religion = additional_info.religion.name_in_arabic if additional_info and additional_info.religion else 'غير متوفر'
        blood_type = additional_info.blood_type if additional_info else 'غير متوفر'
        marital_status = additional_info.get_marital_status_display() if additional_info and additional_info.marital_status else 'غير متوفر'
        governorate = additional_info.governorate_of_residence.name_arabic if additional_info and additional_info.governorate_of_residence else 'غير متوفر'
        address = additional_info.address if additional_info else 'غير متوفر'
        emergency_name = additional_info.emergency_contact_name if additional_info else 'غير متوفر'
        emergency_number = additional_info.emergency_contact_number if additional_info else 'غير متوفر'

        writer.writerow([
            smart_str(employee.username, encoding='utf-8'),
            smart_str(full_name, encoding='utf-8'),
            smart_str(gender, encoding='utf-8'),
            smart_str(nationalism, encoding='utf-8'),
            smart_str(religion, encoding='utf-8'),
            smart_str(blood_type, encoding='utf-8'),
            smart_str(marital_status, encoding='utf-8'),
            smart_str(governorate, encoding='utf-8'),
            smart_str(address, encoding='utf-8'),
            smart_str(emergency_name, encoding='utf-8'),
            smart_str(emergency_number, encoding='utf-8'),
        ])

    return response






########################### Update ############################
from .forms import BloodTypeUpdateForm, ReligionUpdateForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from personalinfo.models import AdditionalInfo
from .forms import NationalismUpdateForm



from django.http import Http404
from personalinfo.models import AdditionalInfo

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from personalinfo.models import AdditionalInfo
from .forms import MaritalStatusUpdateForm





@login_required
@permission_required('personalinfo.can_update_blood_type', raise_exception=True)
def update_blood_type(request, slug):
   
    try:
        # استخدام get بدلاً من filter للحصول على السجل المفرد
        additional_info = AdditionalInfo.objects.get(slug=slug)
    except AdditionalInfo.DoesNotExist:
        raise Http404("المعلومات الإضافية غير موجودة.")
    
    if request.method == 'POST':
        form = BloodTypeUpdateForm(request.POST, instance=additional_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث فصيلة الدم بنجاح.")
            return redirect('accounts:view_profile')  # استبدل بـ URL الصفحة المناسبة
    else:
        form = BloodTypeUpdateForm(instance=additional_info)
    
    return render(request, 'personalinfo/additionainfo/update/update_blood_type.html', {'form': form})


@login_required
@permission_required('personalinfo.can_update_religion', raise_exception=True)
def update_employee_religion(request, slug):
   
    employee_info = get_object_or_404(AdditionalInfo, slug=slug)

    # التحقق من أن النموذج قد تم إرساله
    if request.method == 'POST':
        form = ReligionUpdateForm(request.POST, instance=employee_info)
        
        if form.is_valid():
            form.save()  # حفظ التغييرات في قاعدة البيانات
            return redirect('accounts:view_profile')  # إعادة التوجيه بعد التحديث الناجح
    else:
        form = ReligionUpdateForm(instance=employee_info)

    return render(request, 'personalinfo/additionainfo/update/update_religion.html', {'form': form})

@login_required
@permission_required('personalinfo.can_update_nationalism', raise_exception=True)
def update_nationalism(request, slug):
   
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)
    
    if request.method == 'POST':
        form = NationalismUpdateForm(request.POST, instance=additional_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث القومية بنجاح.")
            return redirect('accounts:view_profile')  # استبدل بـ URL الصفحة المناسبة
    else:
        form = NationalismUpdateForm(instance=additional_info)

    return render(request, 'personalinfo/additionainfo/update/update_nationalism.html', {'form': form})


@login_required
@permission_required('personalinfo.can_update_marital_status', raise_exception=True)
def update_marital_status(request, slug):
   
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)
    
    if request.method == 'POST':
        form = MaritalStatusUpdateForm(request.POST, instance=additional_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الحالة الاجتماعية بنجاح.")
            return redirect('accounts:view_profile')  # استبدل بـ URL الصفحة المناسبة
    else:
        form = MaritalStatusUpdateForm(instance=additional_info)

    return render(request, 'personalinfo/additionainfo/update/update_marital_status.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from personalinfo.models import AdditionalInfo
from .forms import GovernorateOfResidenceUpdateForm

@login_required
@permission_required('personalinfo.can_update_governorate_of_residence', raise_exception=True)
def update_governorate_of_residence(request, slug):
   
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)
    
    if request.method == 'POST':
        form = GovernorateOfResidenceUpdateForm(request.POST, instance=additional_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث مكان الإقامة بنجاح.")
            return redirect('accounts:view_profile')  # استبدل بـ URL الصفحة المناسبة
    else:
        form = GovernorateOfResidenceUpdateForm(instance=additional_info)

    return render(request, 'personalinfo/additionainfo/update/update_governorate_of_residence.html', {'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from personalinfo.models import AdditionalInfo
from .forms import AddressUpdateForm


@login_required
@permission_required('personalinfo.can_update_address', raise_exception=True)
def update_address(request, slug):
   
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)

    if request.method == 'POST':
        form = AddressUpdateForm(request.POST, instance=additional_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث العنوان بنجاح.")
            return redirect('accounts:view_profile')  # استبدل بـ URL الصفحة المناسبة
    else:
        form = AddressUpdateForm(instance=additional_info)

    return render(request, 'personalinfo/additionainfo/update/update_address.html', {'form': form})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from personalinfo.models import AdditionalInfo
from .forms import EmergencyContactUpdateForm

@login_required
@permission_required('personalinfo.can_update_emergency_contact', raise_exception=True)
def update_emergency_contact(request, slug):
  
    additional_info = get_object_or_404(AdditionalInfo, slug=slug)

    if request.method == 'POST':
        form = EmergencyContactUpdateForm(request.POST, instance=additional_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث بيانات الطوارئ بنجاح.")
            return redirect('accounts:view_profile')  # استبدل بـ URL الصفحة المناسبة
    else:
        form = EmergencyContactUpdateForm(instance=additional_info)

    return render(request, 'personalinfo/additionainfo/update/update_emergency_contact.html', {'form': form})
