from django.shortcuts import render

from .models import BasicInfo, OfficialDocuments, AdditionalInfo
from django.db.models import Count

# Create your views here.


# @login_required
def main_personalinfo(request):
    employees_with_basic_info_count = BasicInfo.objects.count()

    most_common_document_type = OfficialDocuments.objects.values('official_documents_type__name_in_arabic')\
        .annotate(employee_count=Count('basic_info'))\
        .order_by('-employee_count')\
        .first()
    
    most_common_blood_type = AdditionalInfo.objects.values('blood_type')\
        .annotate(count=Count('blood_type'))\
        .order_by('-count')\
        .first()
    
    most_common_birth_place = BasicInfo.objects.values('place_of_birth__name_arabic')\
        .annotate(count=Count('place_of_birth'))\
        .order_by('-count')\
        .first()

    
    
    return render(request, 'personalinfo/mainpersonalinfo.html', {
        'employees_with_basic_info_count': employees_with_basic_info_count,
        'most_common_document_type': most_common_document_type,
        'most_common_blood_type': most_common_blood_type,
        'most_common_birth_place': most_common_birth_place,
       
    })
