from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import GovernorateForm, RegionForm, ContinentForm, CountryForm
from .models import Governorate, Region, Continent, Country
from django.db.models import Count, Q


@login_required
def create_country(request):
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            country = form.save(commit=False)
            country.created_by = request.user
            country.save()
            return redirect('locations:country_statistics')
    else:
        form = CountryForm()
    return render(request, 'locations/country/country_form.html', {'form': form})
    
from django.shortcuts import render
from django.db.models import Count
from .models import Country, Continent
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('locations.can_view_country_details', raise_exception=True)
def country_statistics(request):
    results_per_page = request.GET.get('results_per_page', '10')  # القيمة الافتراضية 10

    # التحقق من صحة قيمة النتائج لكل صفحة
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    countries = Country.objects.select_related('continent', 'created_by').all()
    paginator = Paginator(countries, results_per_page)  # تطبيق الترقيم
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    total_countries = Country.objects.count()

    continents = Continent.objects.all()
    selected_continent = request.GET.get('continent', None)

    if selected_continent:
        page_obj = paginator.get_page(page_number)

    context = {
        'total_countries': total_countries,
        'countries': page_obj,  # إرسال الكائن المرقم إلى القالب
        'results_per_page': results_per_page,
        'continents': continents,
        'selected_continent': selected_continent,
    }

    return render(request, 'locations/country/country_statistics.html', context)



import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from .models import Country, Continent

@login_required
def export_countries_csv(request):
    # Get the selected continent from the request
    selected_continent_id = request.GET.get('continent')

    # Create the HTTP response with the CSV content type and UTF-8 encoding
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="countries.csv"'
    response.write('\ufeff'.encode('utf8'))  # Add BOM for Excel compatibility

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row in both Arabic and English for clarity
    writer.writerow([
        smart_str('اسم القارة بالعربي', encoding='utf-8', errors='ignore'),
        smart_str('اسم الدولة بالانكليزي', encoding='utf-8', errors='ignore'),
        smart_str('اسم الدولة بالعربي', encoding='utf-8', errors='ignore'),
        smart_str('مدخل الدولة', encoding='utf-8', errors='ignore'),
        smart_str('ملاحظات', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    # Filter countries based on the selected continent
    if selected_continent_id:
        countries = Country.objects.filter(continent_id=selected_continent_id)
    else:
        countries = Country.objects.all()

    # Write the filtered countries data to the CSV
    for country in countries:
        writer.writerow([
            smart_str(country.continent.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(country.name_english, encoding='utf-8', errors='ignore'),
            smart_str(country.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(country.created_by.get_full_name(), encoding='utf-8', errors='ignore'),
            smart_str(country.description, encoding='utf-8', errors='ignore'),
            smart_str(country.created_at, encoding='utf-8', errors='ignore'),
            smart_str(country.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response



from django.shortcuts import render, get_object_or_404
from .models import Country

@login_required
def country_detail(request, slug):
    # البحث عن الدولة بناءً على الـ slug
    country = get_object_or_404(Country, slug=slug)

    context = {
        'country': country,
    }
    return render(request, 'locations/country/country_detail.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from .models import Country
from .forms import CountryForm

@login_required
def update_country(request, slug):
    # جلب الدولة باستخدام الـ slug
    country = get_object_or_404(Country, slug=slug)
    
    # معالجة النموذج
    if request.method == 'POST':
        form = CountryForm(request.POST, instance=country)
        if form.is_valid():
            form.save()
            return redirect('locations:country_statistics')  # إعادة التوجيه إلى إحصائيات الدول
    else:
        form = CountryForm(instance=country)

    context = {
        'form': form,
        'country': country
    }
    return render(request, 'locations/country/update_country.html', context)



from django.shortcuts import get_object_or_404, redirect
from .models import Continent
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


@login_required
def delete_country(request, slug):
    # التحقق من صلاحيات المستخدم
    if not request.user.has_perm('locations.delete_continent'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    # جلب القارة باستخدام الـ slug
    country = get_object_or_404(Country, slug=slug)
    
    # حذف القارة
    country.delete()
    
    messages.success(request, "تم حذف القارة بنجاح.")
    return redirect('locations:country_statistics')  # يمكنك تغيير الرابط حسب حاجتك




@login_required
def download_sample_countries_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="countries_sample.csv"'

    # إضافة UTF-8 BOM لضمان دعم العربية
    response.write('\ufeff'.encode('utf-8-sig'))
    writer = csv.writer(response)

    # كتابة العناوين بالعربية
    header = ['اسم إنجليزي', 'اسم عربي', 'القارة', 'الوصف']
    writer.writerow(header)

    # كتابة بيانات عينة
    sample_rows = [
        ['China', 'الصين', 'آسيا', 'أكبر دولة في العالم سكاناً'],
        ['Japan', 'اليابان', 'آسيا', 'دولة متقدمة في التكنولوجيا'],
        ['India', 'الهند', 'آسيا', 'ثاني أكبر دولة من حيث عدد السكان'],
        ['Saudi Arabia', 'السعودية', 'آسيا', 'أكبر دولة في شبه الجزيرة العربية']
    ]
    writer.writerows(sample_rows)

    return response


from .forms import CountryCSVUploadForm

# @permission_required('app.can_create_country', raise_exception=True)

import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from .models import Country, Continent

# @permission_required('app.can_create_country', raise_exception=True)
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from .models import Country, Continent


@login_required
def upload_country_csv(request):
    if request.method == 'POST':
        form = CountryCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            try:
                # قراءة محتوى الملف
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                # إزالة BOM من العنوان الأول (إن وجد)
                if reader.fieldnames[0].startswith('\ufeff'):
                    reader.fieldnames[0] = reader.fieldnames[0].replace('\ufeff', '')

                # تحويل reader إلى قائمة والتحقق من التكرارات داخل الملف
                reader = list(reader)
                seen_countries = set()  # مجموعة لتخزين الدول التي تمت معالجتها داخل الملف

                for row in reader:
                    try:
                        # استخراج البيانات
                        name_english = row.get('الدولة بالإنجليزية', '').strip() if row.get('الدولة بالإنجليزية') else None
                        name_arabic = row.get('الدولة بالعربية', '').strip() if row.get('الدولة بالعربية') else None
                        continent_name = row.get('القارة', '').strip() if row.get('القارة') else None
                        description = row.get('الوصف', '').strip() if row.get('الوصف') else None

                        # التحقق من أن الاسم العربي متوفر لأنه إلزامي
                        if not name_arabic:
                            messages.error(request, f"السطر {row} يحتوي على اسم عربي ناقص، وهو مطلوب.")
                            continue

                        # التحقق من التكرار داخل نفس الملف باستخدام الاسم العربي فقط
                        if name_arabic in seen_countries:
                            messages.warning(request, f"تم تخطي الدولة المكررة داخل الملف: {name_arabic}")
                            continue
                        seen_countries.add(name_arabic)

                        # التحقق من التكرار في قاعدة البيانات باستخدام الاسم العربي فقط
                        if Country.objects.filter(name_arabic=name_arabic).exists():
                            messages.warning(request, f"تم تخطي الدولة {name_arabic} لأنها موجودة مسبقًا في قاعدة البيانات.")
                            continue

                        # التحقق من القارة (إذا كانت موجودة)
                        continent = None
                        if continent_name:
                            continent = Continent.objects.filter(name_arabic=continent_name).first()
                            if not continent:
                                messages.warning(request, f"القارة {continent_name} غير موجودة. سيتم إدخال الدولة بدون قارة.")

                        # إدراج الدولة الجديدة
                        created_by = request.user
                        Country.objects.create(
                            name_english=name_english,  # يمكن أن يكون فارغًا
                            name_arabic=name_arabic,
                            description=description,  # يمكن أن يكون فارغًا
                            continent=continent,  # يمكن أن يكون None
                            created_by=created_by
                        )

                    except Exception as e:
                        messages.error(request, f"حدث خطأ أثناء معالجة السطر: {row}. الخطأ: {e}")
                        continue

                messages.success(request, "تم تحميل البيانات بنجاح!")
                return redirect('locations:country_statistics')

            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {e}")
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات.")
    else:
        form = CountryCSVUploadForm()
    
    return render(request, 'locations/country/upload_countries_csv.html', {'form': form})

import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

def export_all_countries_csv(request):
    # إنشاء استجابة HTTP بصيغة CSV مع تعيين نوع المحتوى والترميز
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="countries.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM للتوافق مع Excel

    # إنشاء كائن كاتب CSV
    writer = csv.writer(response)

    # كتابة الصف الرئيسي (Header) بأسماء الأعمدة
    writer.writerow([
        smart_str('اسم الدولة بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم الدولة بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('اسم القارة', encoding='utf-8', errors='ignore'),
        smart_str('مدخل الدولة', encoding='utf-8', errors='ignore'),
        smart_str('الوصف', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    # جلب بيانات الدول وكتابتها في ملف CSV
    for country in Country.objects.select_related('continent', 'created_by').all():
        writer.writerow([
            smart_str(country.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(country.name_english, encoding='utf-8', errors='ignore'),
            smart_str(country.continent.name_arabic, encoding='utf-8', errors='ignore'),
            smart_str(country.created_by.username if country.created_by else '-', encoding='utf-8', errors='ignore'),
            smart_str(country.description, encoding='utf-8', errors='ignore'),
            smart_str(country.created_at, encoding='utf-8', errors='ignore'),
            smart_str(country.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response





