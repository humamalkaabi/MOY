from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count
from rddepartment.models.employee_education_models import EmployeeEducation


# Create your views here.

@login_required
def main_rddepartment(request):

    most_common_degree = EmployeeEducation.objects.values('education_degree_type__name_in_arabic')\
        .annotate(count=Count('education_degree_type'))\
        .order_by('-count')\
        .first()
    
    most_common_college = EmployeeEducation.objects.values('college__name_in_arabic')\
        .annotate(count=Count('college'))\
        .order_by('-count')\
        .first()
    
    most_common_iraqi_university = EmployeeEducation.objects.values('iraqi_university__name_in_arabic')\
        .annotate(count=Count('iraqi_university'))\
        .order_by('-count')\
        .first()
    
    most_common_foreign_university = EmployeeEducation.objects.values('foreign_university__name_in_english')\
        .annotate(count=Count('foreign_university'))\
        .order_by('-count')\
        .first()


    
    context = {
       'most_common_degree': most_common_degree,
       'most_common_college': most_common_college,
       'most_common_iraqi_university': most_common_iraqi_university,
       'most_common_foreign_university': most_common_foreign_university,
    }

    return render(request, 'rddepartment/main_rddepartment.html', context)
