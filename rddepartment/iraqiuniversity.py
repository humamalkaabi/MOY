# import datetime
from django.forms import ValidationError
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Employee
from personalinfo.models import BasicInfo
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
import csv
from locations.models import Country, Governorate
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponseForbidden
import io
from rddepartment.forms.iraqi_universities_forms import IraqiUniversityForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rddepartment.models.universities_models import IraqiUniversity
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

@login_required
def main_iraqiuniversity(request):
    university_type = request.GET.get('university_type', '')
    governorate_id = request.GET.get('governorate', '')
    name_in_arabic = request.GET.get('name_in_arabic', '').strip()
    results_per_page = request.GET.get('results_per_page', '10')  # القيمة الافتراضية لعدد النتائج

    # التأكد من صحة عدد النتائج لكل صفحة
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    universities = IraqiUniversity.objects.all()
    governorates = Governorate.objects.all()

    if university_type:
        universities = universities.filter(university_type=university_type)

    if governorate_id:
        universities = universities.filter(governorate_id=governorate_id)
    
    if name_in_arabic:
        universities = universities.filter(name_in_arabic__icontains=name_in_arabic)
    
    if 'export_csv' in request.GET:
        return export_iraqi_university_to_csv(request)

    paginator = Paginator(universities, results_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    results_count = universities.count()

    context = {
        'universities': page_obj,  # تعديل لتكون صفحة بدلاً من القائمة الكاملة
        'selected_type': university_type,
        'selected_governorate': governorate_id,
        'governorates': governorates,
        'results_count': results_count,
        'searched_name': name_in_arabic,
    }

    return render(request, 'rddepartment/iraqiuniversity/main_iraqiuniversity.html', context)


import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required

@login_required
def export_iraqi_university_to_csv(request):
    # جلب الجامعات بناءً على الفلاتر
    university_type = request.GET.get('university_type', '')
    governorate_id = request.GET.get('governorate', '')
    name_in_arabic = request.GET.get('name_in_arabic', '').strip()

    universities = IraqiUniversity.objects.all()

    if university_type:
        universities = universities.filter(university_type=university_type)

    if governorate_id:
        universities = universities.filter(governorate_id=governorate_id)

    if name_in_arabic:
        universities = universities.filter(name_in_arabic__icontains=name_in_arabic)

    # إعداد ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="iraqi_universities.csv"'

    # إضافة BOM لتوافق مع Excel
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    # كتابة الرأس
    writer.writerow([
        smart_str('ID', encoding='utf-8'),
        smart_str('اسم الجامعة بالعربية', encoding='utf-8'),
        smart_str('اسم الجامعة بالإنجليزية', encoding='utf-8'),
        smart_str('نوع الجامعة', encoding='utf-8'),
        smart_str('المحافظة', encoding='utf-8'),
        smart_str('تاريخ الإنشاء', encoding='utf-8'),
        smart_str('تاريخ التحديث', encoding='utf-8'),
    ])

    # كتابة البيانات
    for university in universities:
        writer.writerow([
            university.id,
            smart_str(university.name_in_arabic, encoding='utf-8'),
            smart_str(university.name_in_english, encoding='utf-8') if university.name_in_english else 'غير متوفر',
            smart_str('حكومية' if university.university_type == IraqiUniversity.GOVERNMENTAL else 'أهلية', encoding='utf-8'),
            smart_str(university.governorate.name_arabic if university.governorate else 'غير متوفر', encoding='utf-8'),
            university.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            university.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@login_required
@permission_required('rddepartment.can_add_iraqi_university', raise_exception=True)
def add_iraqiuniversity(request):
   
    login_user = request.user
    if request.method == 'POST':
        form = IraqiUniversityForm(request.POST)
        if form.is_valid():
            # إعداد الكائن قبل الحفظ
            iraqiuniversity = form.save(commit=False)
            iraqiuniversity.created_by = login_user
            iraqiuniversity.save()
            messages.success(request, "تمت إضافة الجامعة العراقية  بنجاح!")
            return redirect('rddepartment:main_iraqiuniversity')  # عدّل الرابط إذا لزم الأمر
        else:
            messages.error(request, "حدث خطأ أثناء إضافة الجامعة . يرجى المحاولة مرة أخرى.")
    else:
        form = IraqiUniversityForm()

    # تمرير النموذج والسياق إلى القالب
    return render(request, 'rddepartment/iraqiuniversity/add_iraqiuniversity.html', {
        'form': form,
        'login_user': login_user,
    })



def iraqiuniversity_detail(request, slug):
    iraqiuniversity = get_object_or_404(IraqiUniversity, slug=slug)
    return render(request, 'rddepartment/iraqiuniversity/iraqiuniversity_detail.html', {'iraqiuniversity': iraqiuniversity})


@login_required
@permission_required('rddepartment.can_update_iraqi_university', raise_exception=True)
def update_iraqiuniversity(request, slug):
    # Retrieve the specific instance using the slug
    iraqiuniversity = get_object_or_404(IraqiUniversity, slug=slug)
    
    if request.method == 'POST':
        form = IraqiUniversityForm(request.POST, instance=iraqiuniversity)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث  الجامعة العراقية بنجاح!")
            return redirect('rddepartment:main_iraqiuniversity')  # Adjust the URL name as needed
        else:
            messages.error(request, "حدث خطأ أثناء تحديث  الكلية. يرجى المحاولة مرة أخرى.")
    else:
        form = IraqiUniversityForm(instance=iraqiuniversity)
    
    return render(request, 'rddepartment/iraqiuniversity/update_iraqiuniversity.html', {
        'form': form,
        'iraqiuniversity': iraqiuniversity,
    })





@login_required
@permission_required('rddepartment.can_delete_iraqi_university', raise_exception=True)
def delete_iraqiuniversity(request, slug):
    
    iraqiuniversity = get_object_or_404(IraqiUniversity, slug=slug)
    
    iraqiuniversity.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('rddepartment:main_iraqiuniversity')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك



from rddepartment.forms.iraqi_universities_forms import IraqiUniversityCSVUploadForm


import csv
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
@permission_required('rddepartment.can_add_iraqi_university', raise_exception=True)
def upload_iraqi_university_csv(request):
    
    if request.method == 'POST':
        form = IraqiUniversityCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                # قراءة وفك ترميز الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.reader(decoded_file)

                # تخطي الصف الأول (عناوين الأعمدة)
                next(reader)

                for row in reader:
                    try:
                        # قراءة البيانات من الأعمدة
                        name_in_arabic = row[0].strip()
                        name_in_english = row[1].strip() if len(row) > 1 else None
                        university_type = row[2].strip() if len(row) > 2 else None
                        governorate_name = row[3].strip() if len(row) > 3 else None
                        address = row[4].strip() if len(row) > 4 else None

                        # التحقق من صحة نوع الجامعة
                        if university_type not in [IraqiUniversity.GOVERNMENTAL, IraqiUniversity.PRIVATE]:
                            messages.error(request, f"نوع الجامعة '{university_type}' غير صحيح في السطر: {row}")
                            continue

                        # جلب المحافظة
                        try:
                            governorate = Governorate.objects.get(name_arabic=governorate_name)
                        except Governorate.DoesNotExist:
                            messages.error(request, f"المحافظة '{governorate_name}' غير موجودة.")
                            continue

                        # إنشاء أو تحديث الجامعة العراقية
                        IraqiUniversity.objects.update_or_create(
                            name_in_arabic=name_in_arabic,
                            governorate=governorate,
                            defaults={
                                'name_in_english': name_in_english,
                                'university_type': university_type,
                                'address': address,
                                'created_by': request.user if isinstance(request.user, Employee) else None,
                            }
                        )
                    except Exception as e:
                        messages.error(request, f"خطأ أثناء معالجة السطر {row}: {str(e)}")
                        continue

                # رسالة نجاح
                messages.success(request, "تم تحميل الجامعات العراقية بنجاح!")
                return redirect('rddepartment:main_iraqiuniversity')  # تعديل الرابط حسب مشروعك
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء قراءة الملف: {str(e)}")
    else:
        form = IraqiUniversityCSVUploadForm()

    return render(request, 'rddepartment/iraqiuniversity/upload_iraqi_university_csv.html', {'form': form})




@login_required
def download_sample_iraqi_university_csv(request):
    # إعداد الاستجابة بصيغة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="iraqi_universities_sample.csv"'
    
    # دعم UTF-8
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)
    
    # كتابة العناوين
    header = ['اسم الجامعة بالعربية', 'اسم الجامعة بالإنجليزية', 'نوع الجامعة', 'اسم المحافظة', 'عنوان الجامعة']
    writer.writerow(header)
    
    # كتابة بيانات عينة
    sample_rows = [
        ['جامعة بغداد', 'University of Baghdad', 'governmental', 'بغداد', 'منطقة الجادرية'],
        ['جامعة النهرين', 'Al-Nahrain University', 'governmental', 'بغداد', 'الجادرية'],
        ['جامعة الكوفة', 'University of Kufa', 'governmental', 'النجف', 'النجف الأشرف'],
        ['جامعة أهل البيت', 'Ahl Al-Bayt University', 'private', 'كربلاء', 'حي الموظفين']
    ]
    writer.writerows(sample_rows)
    
    return response
# import csv
# from django.http import HttpResponse


# def download_sample_iraqi_university_csv(request):
#     # إعداد الاستجابة ليتم تحميلها كملف CSV مع الترميز المناسب لدعم اللغة العربية
#     response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
#     response['Content-Disposition'] = 'attachment; filename="iraqi_university_sample.csv"'

#     # إعداد كاتب CSV مع الترميز المناسب
#     response.write('\ufeff'.encode('utf-8-sig'))
#     writer = csv.writer(response)

#     # كتابة عناوين الأعمدة (باللغة العربية)
#     header = [
#         'اسم الجامعة باللغة العربية', 
#         'اسم الجامعة باللغة الإنجليزية', 
#         'اسم المحافظة', 
#         'العنوان',
#         'نوع الجامعة'  # إضافة الحقل الجديد "نوع الجامعة"
#     ]
#     writer.writerow(header)

#     # كتابة صفوف البيانات (عينات بيانات ثابتة)
#     sample_rows = [
#         ['الجامعة المستنصرية', 'Al-Mustansiriya University', 'بغداد', 'شارع الجامعة المستنصرية', 'جامعة حكومية'],
#         ['جامعة بغداد', 'University of Baghdad', 'بغداد', 'الكرادة', 'جامعة حكومية'],
#         ['جامعة الموصل', 'University of Mosul', 'بغداد', '   ', 'جامعة حكومية'],
#         ['جامعة النهرين', 'Al-Nahrain University', 'بغداد', 'المنصور', 'جامعة أهلية'],
#     ]
#     writer.writerows(sample_rows)

#     return response

# import csv
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.http import HttpResponse
# from django.db.models import Q
# def upload_iraqi_university_csv(request):
#     if request.method == 'POST':
#         form = ForeignUniversityCSVUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES['csv_file']
#             decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
#             reader = csv.reader(decoded_file)

#             next(reader)  # تخطي السطر الأول الذي يحتوي على العناوين

#             for row in reader:
#                 try:
#                     # التحقق من أن السطر يحتوي على العدد الصحيح من الأعمدة
#                     if len(row) < 5:  # أضفنا 5 بدلاً من 4 لأننا نحتاج إلى حقل نوع الجامعة
#                         print(f"السطر يحتوي على بيانات ناقصة: {row}")
#                         continue

#                     # قراءة البيانات من CSV
#                     name_arabic = row[0].strip() if row[0].strip() else None
#                     name_english = row[1].strip() if row[1].strip() else None
#                     governorate_name = row[2].strip() if row[2].strip() else None
#                     address = row[3].strip() if row[3].strip() else None
#                     university_type_str = row[4].strip().lower() if row[4].strip() else None

#                     # تحديد نوع الجامعة بناءً على القيمة المرفوعة
#                     if university_type_str == 'جامعة حكومية':
#                         university_type = IraqiUniversity.GOVERNMENTAL
#                     elif university_type_str == 'جامعة أهلية':
#                         university_type = IraqiUniversity.PRIVATE
#                     else:
#                         print(f"نوع الجامعة غير معروف في السطر: {row}")
#                         continue  # تخطي السطر إذا كان نوع الجامعة غير معروف

#                     # البحث عن المحافظة
#                     governorate = Governorate.objects.filter(
#                         Q(name_english=governorate_name) | Q(name_arabic=governorate_name)
#                     ).first()

#                     if governorate:
#                         print(f"تم العثور على المحافظة: {governorate.name_english}")
#                     else:
#                         print(f"لم يتم العثور على المحافظة: {governorate_name}")
#                         governorate = None  # في حالة عدم العثور على المحافظة

#                     # إنشاء أو تحديث الجامعة العراقية فقط إذا كان اسم الجامعة موجودًا
#                     if name_arabic:  # تأكد من أن اسم الجامعة بالعربية غير فارغ
#                         university, created = IraqiUniversity.objects.update_or_create(
#                             name_arabic=name_arabic,
#                             governorate=governorate,
#                             defaults={
#                                 'name_english': name_english,
#                                 'address': address,
#                                 'university_type': university_type,  # إضافة نوع الجامعة
#                                 'created_by': request.user if isinstance(request.user, Employee) else None,
#                             }
#                         )
                        
#                         # إذا تم إنشاء الجامعة الجديدة، يتم إنشاء الـ slug الفريد
#                         if created:
#                             university.save()
#                         print(f"تم إنشاء أو تحديث الجامعة: {university.name_arabic}")

#                 except Exception as e:
#                     messages.error(request, f"حدث خطأ في السطر {row}: {e}")
#                     continue

#             messages.success(request, "تم تحميل البيانات بنجاح!")
#             return redirect('rddepartment:main_iraqiuniversity')
#     else:
#         form = ForeignUniversityCSVUploadForm()

#     return render(request, 'rddepartment/foreignUniversity/foreign_university_upload.html', {'form': form})
