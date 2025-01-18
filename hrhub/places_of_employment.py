from hrhub.models.hr_utilities_models import DutyAssignmentOrder, PlaceOfEmployment
from hrhub.forms.hr_utitlity import Duty_Assignment_Order_Form, PlaceOfEmploymentForm
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




@login_required
def list_places_of_employment(request):
    # جلب جميع الأماكن
    places_of_employment = PlaceOfEmployment.objects.all()
    context = {
        'places_of_employment': places_of_employment
    }
    return render(request, 'hrhub/place_of_employment/list_places_of_employment.html', context)

@login_required
def list_children_of_employment(request, parent_slug):
    # الحصول على الكيان الأب باستخدام الـ slug
    parent = get_object_or_404(PlaceOfEmployment, slug=parent_slug)

    # جلب الأبناء المباشرين فقط
    children = parent.sub_titles.all()

    context = {
        'parent': parent,
        'places_of_employment': children,
    }
    return render(request, 'hrhub/place_of_employment/list_children_of_employment.html', context)

@login_required
def place_of_employment_detail(request, slug):
    # جلب مكان العمل باستخدام الـ slug
    place_of_employment = get_object_or_404(PlaceOfEmployment, slug=slug)
    context = {
        'place_of_employment': place_of_employment
    }
    return render(request, 'hrhub/place_of_employment/place_of_employment_detail.html', context)

@login_required
def add_place_of_employment(request):
    if not request.user.has_perm('hrhub.add_place_of_employment'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    if request.method == 'POST':
        form = PlaceOfEmploymentForm(request.POST)
        if form.is_valid():
            place_of_employment = form.save(commit=False)
            place_of_employment.created_by = request.user  # ربط بالمستخدم الذي قام بإنشاء المكان
            place_of_employment.save()
            messages.success(request, "تم إضافة مكان العمل بنجاح.")
            return redirect('hrhub:list_places_of_employment')  # تأكد من تحديث الرابط حسب الحاجة
    else:
        form = PlaceOfEmploymentForm()

    return render(request, 'hrhub/place_of_employment/add_place_of_employment.html', {'form': form})


@login_required
def update_place_of_employment(request, slug):
    if not request.user.has_perm('hrhub.change_place_of_employment'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    place_of_employment = get_object_or_404(PlaceOfEmployment, slug=slug)
    
    if request.method == 'POST':
        form = PlaceOfEmploymentForm(request.POST, instance=place_of_employment)
        if form.is_valid():
            place_of_employment = form.save(commit=False)
            place_of_employment.created_by = request.user  # تحديث المستخدم الذي قام بالتعديل
            place_of_employment.save()
            messages.success(request, "تم تحديث مكان العمل بنجاح.")
            return redirect('hrhub:list_places_of_employment')  # تأكد من تحديث الرابط حسب الحاجة
    else:
        form = PlaceOfEmploymentForm(instance=place_of_employment)

    context = {
        'form': form,
        'place_of_employment': place_of_employment
    }
    return render(request, 'hrhub/place_of_employment/update_place_of_employment.html', context)


@login_required
def delete_place_of_employment(request, slug):
    if not request.user.has_perm('hrhub.delete_place_of_employment'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    place_of_employment = get_object_or_404(PlaceOfEmployment, slug=slug)
    place_of_employment.delete()

    messages.success(request, "تم حذف مكان العمل بنجاح.")
    return redirect('hrhub:list_places_of_employment')  # تأكد من تحديث الرابط حسب الحاجة




from hrhub.forms.hr_utitlity import PlaceOfEmploymentCSVUploadForm


import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify

def upload_place_of_employment_csv(request):
    if request.method == 'POST':
        form = PlaceOfEmploymentCSVUploadForm(request.POST, request.FILES)
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
                    name_in_arabic = row.get('عنوان المؤسسة', '').strip()
                    parent_name = row.get('عنوان المؤسسة الأعلى', '').strip()
                    is_default = row.get('افتراضي', '').strip().lower() == "نعم"
                    description = row.get('وصف الوظيفة', '').strip() if row.get('وصف الوظيفة') else None

                    if not name_in_arabic:
                        messages.error(request, f"اسم المؤسسة مفقود في السطر: {row}.")
                        continue

                    rows.append({
                        'name_in_arabic': name_in_arabic,
                        'parent_name': parent_name,
                        'is_default': is_default,
                        'description': description
                    })

                # معالجة المؤسسات العليا أولاً
                for row in rows:
                    parent_name = row['parent_name']
                    if parent_name:
                        PlaceOfEmployment.objects.get_or_create(
                            name_in_arabic=parent_name,
                            defaults={'slug': slugify(unidecode(parent_name))}
                        )

                # إدخال المؤسسات وربطها بالمؤسسات العليا
                for row in rows:
                    parent = None
                    if row['parent_name']:
                        parent = PlaceOfEmployment.objects.filter(name_in_arabic=row['parent_name']).first()

                    # التحقق من عدم تكرار السجل الافتراضي
                    if row['is_default'] and PlaceOfEmployment.objects.filter(is_default=True).exists():
                        messages.warning(request, f"تم تجاوز السجل '{row['name_in_arabic']}' لأنه يوجد سجل افتراضي بالفعل.")
                        continue

                    PlaceOfEmployment.objects.update_or_create(
                        name_in_arabic=row['name_in_arabic'],
                        defaults={
                            'parent': parent,
                            'is_default': row['is_default'],
                            'description': row['description'],
                            'slug': slugify(unidecode(row['name_in_arabic']))
                        }
                    )

                messages.success(request, "تم تحميل المؤسسات بنجاح!")
                return redirect('hrhub:list_places_of_employment')  # استبدل `place_of_employment_list` بالمسار الصحيح
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = PlaceOfEmploymentCSVUploadForm()

    return render(request, 'hrhub/place_of_employment/upload_place_of_employment_csv.html', {'form': form})
