from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import GovernorateForm, RegionForm, ContinentForm, CountryForm
from .models import Governorate, Region, Continent, Country
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from .models import Region
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
@permission_required('locations.can_create_region', raise_exception=True)
def create_region(request):
    if request.method == 'POST':
        form = RegionForm(request.POST)
        if form.is_valid():
            region = form.save(commit=False)
            region.created_by = request.user
            region.save()
            return redirect('locations:region_statistics')
    else:
        form = RegionForm()
    return render(request, 'locations/region/region_form.html', {'form': form})
    

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.db.models import Q
from django.http import HttpResponseRedirect

def region_statistics(request):
    results_per_page = request.GET.get('results_per_page', '10')
    governorate_id = request.GET.get('governorate', '')
    export = request.GET.get('export', '')

    # إذا كان هناك طلب للتصدير، استدعِ دالة التصدير
    if export == 'csv':
        return export_regions_csv(request)

    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    query = Q()
    if governorate_id:
        query &= Q(governorate__id=governorate_id)

    regions = Region.objects.select_related('governorate', 'created_by').filter(query)
    paginator = Paginator(regions, results_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    total_regions = regions.count()
    governorates = Governorate.objects.all()

    context = {
        'regions': page_obj,
        'total_regions': total_regions,
        'results_per_page': results_per_page,
        'governorates': governorates,
        'selected_governorate': governorate_id,
    }

    return render(request, 'locations/region/region_statistics.html', context)



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

def export_regions_csv(request):
    # Get filters from the request
    governorate_id = request.GET.get('governorate', '')

    # Create the HTTP response with the CSV content type and UTF-8 encoding
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="regions.csv"'
    response.write('\ufeff'.encode('utf8'))  # Add BOM for Excel compatibility

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
        smart_str('اسم المحافظة بالعربي', encoding='utf-8'),
        smart_str('اسم المنطقة بالانكليزي', encoding='utf-8'),
        smart_str('اسم المنطقة بالعربي', encoding='utf-8'),
        smart_str('مدخل المنطقة', encoding='utf-8'),
        smart_str('الوصف', encoding='utf-8'),
        smart_str('تاريخ الإنشاء', encoding='utf-8'),
        smart_str('تاريخ التحديث', encoding='utf-8'),
    ])

    # Apply filters
    regions = Region.objects.all()
    if governorate_id:
        regions = regions.filter(governorate_id=governorate_id)

    # Write the filtered regions data to the CSV
    for region in regions:
        writer.writerow([
            smart_str(region.governorate.name_arabic, encoding='utf-8'),
            smart_str(region.name_english, encoding='utf-8'),
            smart_str(region.name_arabic, encoding='utf-8'),
            smart_str(region.created_by.get_full_name() if region.created_by else 'N/A', encoding='utf-8'),
            smart_str(region.description, encoding='utf-8'),
            smart_str(region.created_at, encoding='utf-8'),
            smart_str(region.updated_at, encoding='utf-8'),
        ])

    return response


def region_detail(request, slug):
    region = get_object_or_404(Region, slug=slug)
    context = {
        'region': region
    }
    return render(request, 'locations/region/region_detail.html', context)



@login_required
@permission_required('locations.can_update_region', raise_exception=True)
def update_region(request, slug):
    if not request.user.has_perm('locations.change_region'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    region = get_object_or_404(Region, slug=slug)
    
    if request.method == 'POST':
        form = RegionForm(request.POST, instance=region)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المنطقة بنجاح.")
            return redirect('locations:region_statistics')
    else:
        form = RegionForm(instance=region)
    
    context = {
        'form': form,
        'region': region
    }
    return render(request, 'locations/region/update_region.html', context)


@login_required
@permission_required('locations.can_delete_region', raise_exception=True)
def delete_region(request, slug):
  
    region = get_object_or_404(Region, slug=slug)
    region.delete()
    
    messages.success(request, "تم حذف المنطقة بنجاح.")
    return redirect('locations:region_statistics')



@login_required
def download_sample_regions_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="regions_sample.csv"'
    
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)
    
    # كتابة العناوين
    header = ['الاسم بالإنجليزية', 'الاسم بالعربية', 'اسم المحافظة بالعربية', 'الوصف']
    writer.writerow(header)
    
    # كتابة بيانات عينة
    sample_rows = [
        ['Adhamiya', 'الأعظمية', 'بغداد', 'منطقة شمال بغداد'],
        ['Al-Zubair', 'الزبير', 'البصرة', 'منطقة جنوب العراق']
    ]
    writer.writerows(sample_rows)
    
    return response

from .forms import RegionCSVUploadForm

@login_required
@permission_required('locations.can_create_region', raise_exception=True)
def upload_regions_csv(request):
    if request.method == 'POST':
        form = RegionCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']

            try:
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.reader(decoded_file)
                
                next(reader)  # تخطي العنوان
                for row in reader:
                    if len(row) < 3:
                        messages.error(request, f"السطر {row} يحتوي على بيانات ناقصة.")
                        continue
                    
                    name_english = row[0].strip()
                    name_arabic = row[1].strip()
                    governorate_name_arabic = row[2].strip()
                    description = row[3].strip() if len(row) > 3 else ""

                    try:
                        governorate = Governorate.objects.get(name_arabic=governorate_name_arabic)
                    except Governorate.DoesNotExist:
                        messages.error(request, f"لم يتم العثور على المحافظة: {governorate_name_arabic}")
                        continue
                    
                    # إنشاء أو تحديث السجل
                    Region.objects.update_or_create(
                        name_arabic=name_arabic,
                        governorate=governorate,
                        defaults={
                            'name_english': name_english,
                            'description': description,
                            'created_by': request.user
                        }
                    )

                messages.success(request, "تم تحميل البيانات بنجاح!")
                return redirect('locations:region_statistics')
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = RegionCSVUploadForm()

    return render(request, 'locations/region/upload_regions_csv.html', {'form': form})



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

def export_all_regions_csv(request):
    # إنشاء استجابة HTTP بصيغة CSV مع تعيين نوع المحتوى والترميز
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="regions.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM للتوافق مع Excel

    # إنشاء كائن كاتب CSV
    writer = csv.writer(response)

    # كتابة الصف الرئيسي (Header) بأسماء الأعمدة
    writer.writerow([
        smart_str('اسم المنطقة بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم المنطقة بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('اسم المحافظة', encoding='utf-8', errors='ignore'),
        smart_str('مدخل المنطقة', encoding='utf-8', errors='ignore'),
        smart_str('الوصف', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    # جلب بيانات المناطق وكتابتها في ملف CSV
    for region in Region.objects.select_related('governorate', 'created_by').all():
        writer.writerow([
            smart_str(region.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(region.name_english, encoding='utf-8', errors='ignore'),
            smart_str(region.governorate.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(region.created_by.username if region.created_by else '-', encoding='utf-8', errors='ignore'),
            smart_str(region.description, encoding='utf-8', errors='ignore'),
            smart_str(region.created_at, encoding='utf-8', errors='ignore'),
            smart_str(region.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response
