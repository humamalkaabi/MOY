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
from locations.models import Country, Governorate, Continent
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponseForbidden
from rddepartment.models.universities_models import ForeignUniversity
import io
from rddepartment.forms.foreignuniversity_forms import ForeignUniversityForm, ForeignUniversityCSVUploadForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


import csv

from django.db.models import Q
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
import csv


@login_required
def main_foreignuniversity(request):
    # جلب جميع الجامعات الأجنبية
    foreignUniversitys = ForeignUniversity.objects.all()

    # جلب القارات والدول (لاستعمالها في الاختيار)
    continents = Continent.objects.all()
    countries = Country.objects.all()

    # تصفية حسب الدولة
    country_id = request.GET.get('country')
    if country_id:
        foreignUniversitys = foreignUniversitys.filter(country_id=country_id)

    # تصفية حسب اسم الجامعة باللغة الإنجليزية
    name_in_english = request.GET.get('name_in_english')
    if name_in_english:
        foreignUniversitys = foreignUniversitys.filter(name_in_english__icontains=name_in_english)

    # تصفية حسب اسم الجامعة بالعربية
    name_arabic = request.GET.get('name_arabic')
    if name_arabic:
        foreignUniversitys = foreignUniversitys.filter(name_in_arabic__icontains=name_arabic)

    # طباعة لتتبع عدد النتائج (للاختبار)
    print(f"Filtered Results Count: {foreignUniversitys.count()}")

    # تمرير البيانات إلى القالب
    context = {
        'foreignUniversitys': foreignUniversitys,
        'countries': countries,
        'continents': continents,
        'foreignuniversitys_count': foreignUniversitys.count(),
    }

    return render(request, 'rddepartment/foreignUniversity/main_foreignuniversitys.html', context)

from django.http import JsonResponse

@login_required
def get_countries_by_continent(request):
    continent_id = request.GET.get('continent_id')
    if continent_id:
        countries = Country.objects.filter(continent_id=continent_id).values('id', 'name_arabic')
        return JsonResponse(list(countries), safe=False)
    return JsonResponse([], safe=False)



@login_required
@permission_required('rddepartment.can_add_foreign_university', raise_exception=True)
def add_foreignuniversity(request):
    if request.method == 'POST':
        form = ForeignUniversityForm(request.POST)
        if form.is_valid():
            foreignuniversity = form.save(commit=False)
            foreignuniversity.created_by = request.user
            foreignuniversity.save()          
            messages.success(request, 'تم إضافة الجامعة بنجاح.')
            return redirect('rddepartment:main_foreignuniversity')
    else:
        form = ForeignUniversityForm()
    return render(request, 'rddepartment/foreignUniversity/add_foreignuniversity.html', {'form': form})

from django.views import View

@login_required
def foreignuniversitys_detail(request, slug):
    foreignuniversity = get_object_or_404(ForeignUniversity, slug=slug)
    return render(request, 'rddepartment/foreignUniversity/foreignuniversitys_detail.html', {'foreignuniversity': foreignuniversity})

from rddepartment.forms.foreignuniversity_forms import ForeignUniversityUpdateForm


@login_required
@permission_required('rddepartment.can_update_foreign_university', raise_exception=True)
def update_foreignuniversitys(request, slug):
    # Retrieve the specific instance using the slug
    foreignUniversity = get_object_or_404(ForeignUniversity, slug=slug)
    
    if request.method == 'POST':
        form = ForeignUniversityUpdateForm(request.POST, instance=foreignUniversity)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث نوع الشهادة بنجاح!")
            return redirect('rddepartment:main_foreignuniversity')  # Adjust the URL name as needed
        else:
            messages.error(request, "حدث خطأ أثناء تحديث نوع الشهادة. يرجى المحاولة مرة أخرى.")
    else:
        form = ForeignUniversityUpdateForm(instance=foreignUniversity)
    
    return render(request, 'rddepartment/foreignUniversity/update_foreignuniversity.html', {
        'form': form,
        'foreignUniversity': foreignUniversity,
    })




from rddepartment.forms.foreignuniversity_forms import ForeignUniversityCSVUploadForm


import csv
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
@permission_required('rddepartment.can_add_foreign_university', raise_exception=True)
def upload_foreign_university_csv(request):
   
    if request.method == 'POST':
        form = ForeignUniversityCSVUploadForm(request.POST, request.FILES)
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
                        name_in_english = row[0].strip()
                        name_in_arabic = row[1].strip() if len(row) > 1 else ''
                        abbreviation = row[2].strip() if len(row) > 2 else ''
                        university_link = row[3].strip() if len(row) > 3 else ''
                        country_name = row[4].strip() if len(row) > 4 else None

                        # التحقق من وجود اسم الدولة
                        if not country_name:
                            messages.error(request, f"اسم الدولة مفقود في السطر: {row}")
                            continue

                        # تنظيف اسم الدولة
                        country_name = country_name.strip()

                        # جلب الدولة المرتبطة
                        try:
                            country = Country.objects.get(name_arabic=country_name)
                        except Country.DoesNotExist:
                            messages.error(request, f"الدولة '{country_name}' غير موجودة.")
                            continue

                        # إنشاء أو تحديث الجامعة الأجنبية
                        ForeignUniversity.objects.update_or_create(
                            name_in_english=name_in_english,
                            country=country,
                            defaults={
                                'name_in_arabic': name_in_arabic,
                                'university_name_abbreviation': abbreviation,
                                'university_link': university_link,
                                'created_by': request.user if isinstance(request.user, Employee) else None,
                            }
                        )
                    except Exception as e:
                        messages.error(request, f"خطأ أثناء معالجة السطر {row}: {str(e)}")
                        continue

                # رسالة نجاح
                messages.success(request, "تم تحميل الجامعات الأجنبية بنجاح!")
                return redirect('rddepartment:main_foreignuniversity')  # تعديل الرابط وفقًا لمشروعك
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء قراءة الملف: {str(e)}")
    else:
        form = ForeignUniversityCSVUploadForm()

    return render(request, 'rddepartment/foreignUniversity/foreign_university_upload.html', {'form': form})



@login_required
def download_sample_foreign_universities_csv(request):
    # إعداد الاستجابة بصيغة CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="foreign_universities_sample.csv"'
    
    # دعم UTF-8
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)
    
    # كتابة العناوين
    header = ['اسم الجامعة بالإنجليزية', 'اسم الجامعة بالعربية', 'اختصار الاسم', 'الرابط الإلكتروني', 'اسم الدولة بالعربية']
    writer.writerow(header)
    
    # كتابة بيانات عينة
    sample_rows = [
        ['University of Oxford', 'جامعة أكسفورد', 'OXF', 'https://ox.ac.uk', 'المملكة المتحدة'],
        ['Harvard University', 'جامعة هارفارد', 'HAR', 'https://harvard.edu', 'الولايات المتحدة الأمريكية']
    ]
    writer.writerows(sample_rows)
    
    return response



@login_required
@permission_required('rddepartment.can_delete_foreign_university', raise_exception=True)
def delete_foreignuniversity(request, slug):
    # التحقق من صلاحيات المستخدم
    
    
    foreignUniversity = get_object_or_404(ForeignUniversity, slug=slug)
    
    foreignUniversity.delete()
    
    messages.success(request, "تم حذف نوع الشهادة بنجاح.")
    return redirect('rddepartment:main_foreignuniversity')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك


