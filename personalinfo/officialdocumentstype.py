# views.py
from django.shortcuts import render
from .models import Official_Documents_Type
from django.db.models import Count

from django.shortcuts import render, redirect
from .forms import OfficialDocumentsTypeForm
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404


import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.db.models import Count

import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied



def main_official_documents_type(request):
    documents = Official_Documents_Type.objects.annotate(employee_count=Count('official_documents_type'))

    documents_type = Official_Documents_Type.objects.all()
    documents_type_count = documents_type.count()

    return render(request, 'personalinfo/official_documents/documents_type/main_official_documents.html', {'documents': documents,
                                                                                                           'documents_type_count': documents_type_count})

@login_required
@permission_required('personalinfo.can_create_official_documents_type', raise_exception=True)
def add_official_document(request):
    if request.method == 'POST':
        form = OfficialDocumentsTypeForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user  # إضافة المستخدم الذي أنشأ الوثيقة
            document.save()
            messages.success(request, "تم إضافة الوثيقة بنجاح.")
            return redirect('personalinfo:main_official_documents_type')
    else:
        form = OfficialDocumentsTypeForm()
    
    return render(request, 'personalinfo/official_documents/documents_type/add_official_document.html', {'form': form,
                                                                                                         'created_by': request.user})



def document_detail(request, slug):
    document = get_object_or_404(Official_Documents_Type, slug=slug)
    employee_count = document.official_documents_type.count()
    return render(request, 'personalinfo/official_documents/documents_type/document_detail.html', {'document': document,
                                                                                                  'employee_count': employee_count })


@login_required
@permission_required('personalinfo.can_update_official_documents_type', raise_exception=True)
def update_official_document(request, slug):
    document = get_object_or_404(Official_Documents_Type, slug=slug)
    
    if request.method == 'POST':
        form = OfficialDocumentsTypeForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الوثيقة بنجاح.")
            return redirect('personalinfo:main_official_documents_type')
    else:
        form = OfficialDocumentsTypeForm(instance=document)
    
    return render(request, 'personalinfo/official_documents/documents_type/update_official_document.html', {'form': form,
                                                                                                             'document': document,
                                                                                                              'created_by': request.user})

@login_required
@permission_required('personalinfo.can_delete_official_documents_type', raise_exception=True)
def delete_official_document_type(request, slug):
    document = get_object_or_404(Official_Documents_Type, slug=slug)
    
    
    document.delete()
    messages.success(request, "تم حذف الوثيقة بنجاح.")
    return redirect('personalinfo:main_official_documents_type')



from django.http import HttpResponse
from django.utils.encoding import smart_str
from unidecode import unidecode

@login_required
def export_official_documents_csv(request):
    # إنشاء استجابة HTTP بصيغة CSV مع تعيين نوع المحتوى والترميز
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="official_documents.csv"'
    response.write('\ufeff'.encode('utf8'))  # إضافة BOM للتوافق مع Excel

    # إنشاء كائن كاتب CSV
    writer = csv.writer(response)

    # كتابة الصف الرئيسي (Header) بأسماء الأعمدة
    writer.writerow([
        smart_str('اسم الوثيقة بالعربية', encoding='utf-8', errors='ignore'),
        smart_str('اسم الوثيقة بالإنجليزية', encoding='utf-8', errors='ignore'),
        smart_str('ملاحظات عن الوثيقة', encoding='utf-8', errors='ignore'),
        smart_str('مدخل البيانات', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ الإنشاء', encoding='utf-8', errors='ignore'),
        smart_str('تاريخ التحديث', encoding='utf-8', errors='ignore'),
    ])

    # جلب بيانات الوثائق الرسمية وكتابتها في ملف CSV
    for document in Official_Documents_Type.objects.select_related('created_by').all():
        writer.writerow([
            smart_str(document.name_in_arabic if document.name_in_arabic else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(document.name_in_english if document.name_in_english else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(document.commennts if document.commennts else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(document.created_by.username if document.created_by else 'فارغة', encoding='utf-8', errors='ignore'),
            smart_str(document.created_at, encoding='utf-8', errors='ignore'),
            smart_str(document.updated_at, encoding='utf-8', errors='ignore'),
        ])

    return response
