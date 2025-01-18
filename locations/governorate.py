# views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Governorate, Region, Continent, Country
from .forms import GovernorateForm, RegionForm, ContinentForm, CountryForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.text import slugify
from unidecode import unidecode
from .models import Governorate, Region, Continent, Country
from django.db.models import Count, Q
from accounts.models import Employee
import csv
from django.http import HttpResponse
from .models import Governorate
from .forms import GovernorateCSVUploadForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from .models import Governorate
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


# Governorate Views

@login_required
@permission_required('locations.can_reate_governorate', raise_exception=True)
def create_governorate(request):
    if request.method == 'POST':
        form = GovernorateForm(request.POST)
        if form.is_valid():
            governorate = form.save(commit=False)
            governorate.created_by = request.user  # Assuming `request.user` is an instance of `Employee`
            governorate.save()
            return redirect('locations:governorate_statistics')  # Replace with your success URL
    else:
        form = GovernorateForm()
    return render(request, 'locations/governorate/governorate_create_form.html', {'form': form})


@login_required
@permission_required('locations.can_view_governorate_details', raise_exception=True)
def governorate_statistics(request):
    results_per_page = request.GET.get('results_per_page', '10')  # القيمة الافتراضية 10

    # التحقق من صحة قيمة النتائج لكل صفحة
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    governorates = Governorate.objects.all()
    paginator = Paginator(governorates, results_per_page)  # تطبيق الترقيم
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    total_governorates = Governorate.objects.count()

    context = {
        'total_governorates': total_governorates,
        'governorates': page_obj,  # إرسال الكائن المرقم إلى القالب
        'results_per_page': results_per_page,
    }

    return render(request, 'locations/governorate/governorate_statistics.html', context)



def export_governorates_csv(request):
    # Create the HTTP response with the CSV content type and UTF-8 encoding
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="governorates.csv"'
    response.write('\ufeff'.encode('utf8'))  # Add BOM for Excel compatibility

    # Create a CSV writer object
    writer = csv.writer(response)
    
    # Write the header row in both Arabic and English for clarity
    writer.writerow([
        smart_str('اسم المحافظة بالعربي', encoding='utf-8', errors='ignore'),
        smart_str('اسم المحافظة بالانكليزي', encoding='utf-8', errors='ignore'),
        smart_str('مدخل المحافظة', encoding='utf-8', errors='ignore'),
        smart_str('الوصف', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    # Query the governorates and write their data to the CSV
    for governorate in Governorate.objects.all():
        writer.writerow([
            smart_str(governorate.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(governorate.name_english, encoding='utf-8', errors='ignore'),
            smart_str(governorate.created_by.username, encoding='utf-8', errors='ignore'),
            smart_str(governorate.description, encoding='utf-8', errors='ignore'),
            smart_str(governorate.created_at, encoding='utf-8', errors='ignore'),
            smart_str(governorate.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response



def governorate_detail(request, slug):
    # جلب سجل المحافظة باستخدام slug
    governorate = get_object_or_404(Governorate, slug=slug)
    context = {
        'governorate': governorate
    }
    return render(request, 'locations/governorate/governorate_detail.html', context)



@login_required
@permission_required('locations.can_update_governorate', raise_exception=True)
def update_governorate(request, slug):
    # التحقق من صلاحيات المستخدم
    
    
    # جلب سجل المحافظة باستخدام الـ slug
    governorate = get_object_or_404(Governorate, slug=slug)
    
    # التحقق إذا كانت الـ POST تحتوي على البيانات لتحديث السجل
    if request.method == 'POST':
        form = GovernorateForm(request.POST, instance=governorate)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المحافظة بنجاح.")
            return redirect('locations:governorate_statistics')  # يمكن تعديل الرابط
    else:
        form = GovernorateForm(instance=governorate)

    context = {
        'form': form,
        'governorate': governorate
    }
    return render(request, 'locations/governorate/update_governorate.html', context)



@login_required
@permission_required('locations.can_delete_governorate', raise_exception=True)
def delete_governorate(request, slug):
  
    # جلب سجل المحافظة باستخدام الـ slug
    governorate = get_object_or_404(Governorate, slug=slug)
    
    # حذف السجل
    governorate.delete()
    
    messages.success(request, "تم حذف المحافظة بنجاح.")
    return redirect('locations:governorate_statistics')





@login_required
def download_sample_governorates_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="governorates_sample.csv"'
    
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)
    
    # كتابة العناوين
    header = ['الاسم بالإنجليزية', 'الاسم بالعربية', 'الوصف']
    writer.writerow(header)
    
    # كتابة بيانات عينة
    sample_rows = [
        ['Baghdad', 'بغداد', 'العاصمة العراقية'],
        ['Basrah', 'البصرة', 'ميناء العراق الرئيسي']
    ]
    writer.writerows(sample_rows)
    
    return response

@login_required
@permission_required('locations.can_reate_governorate', raise_exception=True)
def upload_governorates_csv(request):
    
    
    if request.method == 'POST':
        form = GovernorateCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']

            try:
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.reader(decoded_file)
                
                next(reader)  # تخطي العنوان
                for row in reader:
                    if len(row) < 2:
                        messages.error(request, f"السطر {row} يحتوي على بيانات ناقصة.")
                        continue
                    
                    name_english = row[0].strip()
                    name_arabic = row[1].strip()
                    description = row[2].strip() if len(row) > 2 else ""
                    
                    # توليد سلاج فريد
                    base_slug = slugify(unidecode(name_arabic))
                    unique_slug = base_slug
                    count = 1
                    while Governorate.objects.filter(slug=unique_slug).exists():
                        unique_slug = f"{base_slug}-{count}"
                        count += 1
                    
                    # إنشاء أو تحديث السجل
                    Governorate.objects.update_or_create(
                        name_arabic=name_arabic,
                        defaults={
                            'name_english': name_english,
                            'description': description,
                            'slug': unique_slug,
                            'created_by': request.user
                        }
                    )

                messages.success(request, "تم تحميل البيانات بنجاح!")
                return redirect('locations:governorate_statistics')
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = GovernorateCSVUploadForm()

    return render(request, 'locations/governorate/upload_governorates_csv.html', {'form': form})



def download_all_governorates_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="all_governorates.csv"'
    
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)
    
    # كتابة العناوين
    header = ['الاسم بالإنجليزية', 'الاسم بالعربية', 'الوصف']
    writer.writerow(header)
    
    # كتابة بيانات جميع المحافظات
    all_rows = [
        ['Baghdad', 'بغداد', 'العاصمة العراقية'],
        ['Basrah', 'البصرة', 'ميناء العراق الرئيسي'],
        ['Nineveh', 'نينوى', 'مدينة الموصل وأثرها التاريخي'],
        ['Anbar', 'الأنبار', 'أكبر المحافظات مساحة'],
        ['Dhi Qar', 'ذي قار', 'موقع أورو التاريخية'],
        ['Maysan', 'ميسان', 'غنية بالمناطق الزراعية'],
        ['Babil', 'بابل', 'موقع مدينة بابل الأثرية'],
        ['Karbala', 'كربلاء', 'مركز ديني مهم'],
        ['Najaf', 'النجف', 'تضم مرقد الإمام علي'],
        ['Kirkuk', 'كركوك', 'مدينة متعددة الثقافات'],
        ['Erbil', 'أربيل', 'عاصمة إقليم كردستان العراق'],
        ['Duhok', 'دهوك', 'إحدى محافظات كردستان'],
        ['Sulaymaniyah', 'السليمانية', 'مركز ثقافي وتعليمي'],
        ['Salah al-Din', 'صلاح الدين', 'تضم مدينة سامراء التاريخية'],
        ['Wasit', 'واسط', 'مشهورة بالزراعة'],
        ['Qadisiyah', 'القادسية', 'معروفة بمعركتها التاريخية'],
        ['Muthanna', 'المثنى', 'أقل المحافظات سكانًا'],
        ['Diyala', 'ديالى', 'معروفة ببساتين البرتقال'],
    ]
    writer.writerows(all_rows)
    
    return response
