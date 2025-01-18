from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import GovernorateForm, RegionForm, ContinentForm, CountryForm
from .models import Governorate, Region, Continent, Country
from django.db.models import Count, Q
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
@permission_required('locations.can_create_continent', raise_exception=True)
def create_continent(request):
    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.save(commit=False)
            continent.created_by = request.user
            continent.save()
            return redirect('locations:continent_statistics')
    else:
        form = ContinentForm()
    return render(request, 'locations/continent/continent_form.html', {'form': form})



@login_required
@permission_required('locations.can_view_continent', raise_exception=True)
def continent_statistics(request):
    # Query to get the total number of continents
    total_continents = Continent.objects.count()
    continents = Continent.objects.all()
    
   

    context = {
        'total_continents': total_continents,
        
        'continents': continents,
    }
    return render(request, 'locations/continent/continent_statistics.html', context)


import csv
from django.http import HttpResponse
from .models import Continent

import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from .models import Continent

def export_continents_csv(request):
    # Create the HTTP response with the CSV content type and UTF-8 encoding
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="continents.csv"'
    response.write('\ufeff'.encode('utf8'))  # Add BOM for Excel compatibility

    # Create a CSV writer object
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow([
        smart_str('Continent Name (English)', encoding='utf-8', errors='ignore'),
        smart_str('Continent Name (Arabic)', encoding='utf-8', errors='ignore'),
        smart_str('Created By', encoding='utf-8', errors='ignore'),
        smart_str('Description', encoding='utf-8', errors='ignore'),
        smart_str('Created At', encoding='utf-8', errors='ignore'),
        smart_str('Updated At', encoding='utf-8', errors='ignore'),
    ])

    # Query the continents and write their data to the CSV
    for continent in Continent.objects.all():
        writer.writerow([
            smart_str(continent.name_english, encoding='utf-8', errors='ignore'),
            smart_str(continent.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(continent.created_by.get_full_name() if continent.created_by else 'N/A', encoding='utf-8', errors='ignore'),
            smart_str(continent.description, encoding='utf-8', errors='ignore'),
            smart_str(continent.created_at, encoding='utf-8', errors='ignore'),
            smart_str(continent.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response



from django.shortcuts import render, get_object_or_404
from .models import Continent
from django.contrib.auth.decorators import login_required

@login_required
@permission_required('locations.can_view_continent', raise_exception=True)
def continent_detail(request, slug):
    # جلب القارة باستخدام الـ slug
    continent = get_object_or_404(Continent, slug=slug)
    
    context = {
        'continent': continent,
    }
    
    return render(request, 'locations/continent/continent_detail.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from .models import Continent
from .forms import ContinentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
@permission_required('locations.can_update_continent', raise_exception=True)
def update_continent(request, slug):
    # التحقق من صلاحيات المستخدم
    if not request.user.has_perm('locations.change_continent'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    # جلب القارة باستخدام الـ slug
    continent = get_object_or_404(Continent, slug=slug)
    
    if request.method == 'POST':
        form = ContinentForm(request.POST, instance=continent)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث القارة بنجاح.")
            return redirect('locations:continent_statistics')  # يمكنك تغيير الرابط حسب حاجتك
    else:
        form = ContinentForm(instance=continent)
    
    context = {
        'form': form,
        'continent': continent,
    }
    
    return render(request, 'locations/continent/update_continent.html', context)



from django.shortcuts import get_object_or_404, redirect
from .models import Continent
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
@permission_required('locations.can_delete_continent', raise_exception=True)
def delete_continent(request, slug):
    # التحقق من صلاحيات المستخدم
    if not request.user.has_perm('locations.delete_continent'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    # جلب القارة باستخدام الـ slug
    continent = get_object_or_404(Continent, slug=slug)
    
    # حذف القارة
    continent.delete()
    
    messages.success(request, "تم حذف القارة بنجاح.")
    return redirect('locations:continent_statistics')  # يمكنك تغيير الرابط حسب حاجتك




import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

@login_required
def export_all_continents_csv(request):
    # إنشاء استجابة HTTP بصيغة CSV مع تعيين نوع المحتوى والترميز
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="continents.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM للتوافق مع Excel

    # إنشاء كائن كاتب CSV
    writer = csv.writer(response)

    # كتابة الصف الرئيسي (Header) بأسماء الأعمدة
    writer.writerow([
        smart_str('اسم القارة بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم القارة بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('مدخل القارة', encoding='utf-8', errors='ignore'),
        smart_str('الوصف', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    # جلب بيانات القارات وكتابتها في ملف CSV
    for continent in Continent.objects.select_related('created_by').all():
        writer.writerow([
            smart_str(continent.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(continent.name_english, encoding='utf-8', errors='ignore'),
            smart_str(continent.created_by.username if continent.created_by else '-', encoding='utf-8', errors='ignore'),
            smart_str(continent.description, encoding='utf-8', errors='ignore'),
            smart_str(continent.created_at, encoding='utf-8', errors='ignore'),
            smart_str(continent.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response
