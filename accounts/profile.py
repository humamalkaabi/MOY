from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from accounts.models import Employee
from personalinfo.models import BasicInfo, AdditionalInfo, OfficialDocuments
from rddepartment.models.employee_education_models import EmployeeEducation
from rddepartment.models.course_certificate_models import EmployeeCourseCertificate
from hrhub.models.office_position_models import EmployeeOffice
from hrhub.models.staffing_structure_models import EmployeeStaffKind
from hrhub.models.central_financial_allocations_models import CentralFinancialAllocations


@login_required
def view_profile(request):
    user = request.user

    latest_certificate = None  # متغير لحفظ أحدث شهادة
    latest_course_certificate = None
    latest_office_position = None 
    latest_staff_type = None 
    latest_financial_allocation = None  # أحدث مخصصات مالية مركزية

    try:
        basic_info = BasicInfo.objects.get(emp_id=user)
        basic_info_slug = basic_info.slug
        latest_certificate = EmployeeEducation.get_latest_certificate(basic_info)
        latest_course_certificate = EmployeeCourseCertificate.objects.filter(
            basic_info=basic_info
        ).order_by('-date_issued').first()

        latest_office_position = EmployeeOffice.objects.filter(
            basic_info=basic_info
        ).order_by('-start_date').first()

        latest_staff_type = EmployeeStaffKind.objects.filter(
            basic_info=basic_info
        ).order_by('-created_at').first()
        latest_financial_allocation = CentralFinancialAllocations.objects.filter(
            basic_info=basic_info
        ).order_by('-effective_time').first()



        try:
            additional_info = AdditionalInfo.objects.get(basic_info=basic_info)
        except AdditionalInfo.DoesNotExist:
            additional_info = None
        
        documents = OfficialDocuments.objects.filter(basic_info=basic_info)

    except BasicInfo.DoesNotExist:
        basic_info = None
        basic_info_slug = None
        additional_info = None
        documents = None
        
    return render(request, 'accounts/profile/viewprofile.html', {
        'basic_info': basic_info, 
        'basic_info_slug': basic_info_slug,
        'additional_info': additional_info, 
        'documents': documents,
       'user': user, 
        'user_slug': user.slug,  # تأكد من تمرير السلاجي
        'latest_certificate': latest_certificate, 
        'latest_course_certificate': latest_course_certificate,
        'latest_office_position': latest_office_position,
          'latest_staff_type': latest_staff_type,
        'latest_financial_allocation': latest_financial_allocation,  # أحدث دائرة يعمل بها
    })



