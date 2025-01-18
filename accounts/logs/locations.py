from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from locations.models import (
    GovernorateChangeLog,
    RegionChangeLog,
    ContinentChangeLog,
    CountryChangeLog
)

@login_required
def governorate_change_log(request):
    """
    عرض جميع سجلات تغييرات المحافظات مع دعم البحث والتصفية.
    """
    change_logs = GovernorateChangeLog.objects.select_related('governorate', 'user').order_by('-timestamp')

    # تصفية النتائج حسب بيانات البحث
    governorate_name = request.GET.get('governorate_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if governorate_name:
        change_logs = change_logs.filter(governorate__name_arabic__icontains=governorate_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    # تقسيم النتائج إلى صفحات
    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/locations/governorate_change_log.html', context)


@login_required
def region_change_log(request):
    """
    عرض جميع سجلات تغييرات المناطق مع دعم البحث والتصفية.
    """
    change_logs = RegionChangeLog.objects.select_related('region', 'user').order_by('-timestamp')

    region_name = request.GET.get('region_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if region_name:
        change_logs = change_logs.filter(region__name_arabic__icontains=region_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/locations/region_change_log.html', context)


@login_required
def continent_change_log(request):
    """
    عرض جميع سجلات تغييرات القارات مع دعم البحث والتصفية.
    """
    change_logs = ContinentChangeLog.objects.select_related('continent', 'user').order_by('-timestamp')

    continent_name = request.GET.get('continent_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if continent_name:
        change_logs = change_logs.filter(continent__name_arabic__icontains=continent_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/locations/continent_change_log.html', context)


@login_required
def country_change_log(request):
    """
    عرض جميع سجلات تغييرات الدول مع دعم البحث والتصفية.
    """
    change_logs = CountryChangeLog.objects.select_related('country', 'user').order_by('-timestamp')

    country_name = request.GET.get('country_name')
    action = request.GET.get('action')
    user = request.GET.get('user')

    if country_name:
        change_logs = change_logs.filter(country__name_arabic__icontains=country_name)
    if action:
        change_logs = change_logs.filter(action=action)
    if user:
        change_logs = change_logs.filter(user__username__icontains=user)

    paginator = Paginator(change_logs, request.GET.get('results_per_page', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'change_logs': page_obj,
        'results': change_logs.count()
    }
    
    return render(request, 'accounts/logs/locations/country_change_log.html', context)
