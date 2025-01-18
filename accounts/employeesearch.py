from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import Employee
from hrhub.models.office_position_models import Office
from personalinfo.models import Official_Documents_Type, Religion, Nationalism
from rddepartment.models.Education_Degree_Type import EducationDegreeType
from rddepartment.models.course_certificate_models import CourseCertificateType
from hrhub.models.central_financial_allocations_models import CentralFinancialAllocationsType
from hrhub.models.employement_models import EmployementType
from hrhub.models.staffing_structure_models import StaffStructerType, PayrollBudgetType
from hrhub.models.thanks_punishment_absence_models import ThanksType, PunishmentType, AbsenceType
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


@login_required
@permission_required('personalinfo.can_quick_search', raise_exception=True)
def mainemployeesearch(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    office_query = request.GET.get('office', '')
    document_type_query = request.GET.get('document_type', '') 
    religion_query = request.GET.get('religion', '')  # 🔹 تصفية حسب الدين
    nationalism_query = request.GET.get('nationalism', '')
    education_degree_query = request.GET.get('education_degree', '')
    course_certificate_query = request.GET.get('course_certificate', '') 
    central_financial_allocation_query = request.GET.get('central_financial_allocation', '')  # ✅ 
    employment_type_query = request.GET.get('employment_type', '')
    position_type_query = request.GET.get('position_type', '')  # ✅    
    placement_type_query = request.GET.get('placement_type', '')
    staff_structure_type_query = request.GET.get('staff_structure_type', '')
    payroll_budget_query = request.GET.get('payroll_budget_type', '')
    thanks_type_query = request.GET.get('thanks_type', '')
    punishment_type_query = request.GET.get('punishment_type', '')
    absence_type_query = request.GET.get('absence_type', '')
    results_per_page = request.GET.get('results_per_page', '10')

    # التحقق من نتائج لكل صفحة
    try:
        results_per_page = int(results_per_page)
        if results_per_page <= 0:
            results_per_page = 10
    except ValueError:
        results_per_page = 10

    # بناء الاستعلامات
    query = Q()

    if username_query:
        query &= Q(username__icontains=username_query)
    if firstname_query or secondname_query or thirdname_query:
        query &= (
            Q(basic_info__firstname__icontains=firstname_query) |
            Q(basic_info__secondname__icontains=secondname_query) |
            Q(basic_info__thirdname__icontains=thirdname_query)
        )
    if has_basicinfo:
        query &= Q(basic_info__isnull=(has_basicinfo.lower() == 'no'))
    if gender_query:
        query &= Q(basic_info__gender=gender_query)
    if has_phone:
        query &= Q(basic_info__phone_number__isnull=(has_phone.lower() == 'no'))

    if document_type_query:
        query &= Q(basic_info__employee_official_documents__official_documents_type__id=document_type_query)
    
    if religion_query:
        query &= Q(basic_info__additional_info__religion__id=religion_query)  # 🔹 تصفية حسب الدين
    if nationalism_query:
        query &= Q(basic_info__additional_info__nationalism__id=nationalism_query)
    if education_degree_query:
        query &= Q(basic_info__employee_education__education_degree_type__id=education_degree_query)
    
    if course_certificate_query:
        query &= Q(basic_info__employee_course_certificate__coursecertificatetype__id=course_certificate_query)
    
    if central_financial_allocation_query:
        query &= Q(basic_info__allocations__centralfinancialallocationstype__id=central_financial_allocation_query)
    
    if employment_type_query:
        query &= Q(basic_info__employment_histories__employee_type__id=employment_type_query)
    
    if position_type_query:
        query &= Q(basic_info__employee_office_positions__is_primary=(position_type_query == "primary"))
    
    if placement_type_query:
        query &= Q(basic_info__employee_placement__placement_type=placement_type_query)
    
    if staff_structure_type_query:
        query &= Q(basic_info__employee_staff_kind__employee_staff_type__id=staff_structure_type_query)
    
    if payroll_budget_query:
        query &= Q(basic_info__employee_staff_kind__employee_staff_type__payroll_budget_type__id=payroll_budget_query)  # 🔹 تصفية حسب نوع الموازنة
    
    if thanks_type_query:
        query &= Q(basic_info__thanks_letters__thanks_type__id=thanks_type_query)
    
    if punishment_type_query:
        query &= Q(basic_info__employee_punishment_recipients__punishment_type__id=punishment_type_query)

    if absence_type_query:
        query &= Q(basic_info__employee_absence_recipients__absence_type__id=absence_type_query)  





    # تصفية بناءً على الدائرة والدوائر المرتبطة
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    employees = Employee.objects.filter(query).distinct().order_by('username')
    document_types = Official_Documents_Type.objects.all()
    religions = Religion.objects.all()  # 🔹 جلب قائمة الأديان
    nationalisms = Nationalism.objects.all()  # 🔹 جلب قائمة القوميات
    education_degrees = EducationDegreeType.objects.all()
    course_certificates = CourseCertificateType.objects.all()
    financial_allocations = CentralFinancialAllocationsType.objects.all()  # ✅ 
    employment_types = EmployementType.objects.all()  # ✅
    staff_structure_types = StaffStructerType.objects.all()
    payroll_budget_types = PayrollBudgetType.objects.all()
    thanks_types = ThanksType.objects.all()
    punishment_types = PunishmentType.objects.all()
    absence_types = AbsenceType.objects.all()
    

    # التقسيم إلى صفحات
    paginator = Paginator(employees, results_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # جلب الوحدات الإدارية الجذرية أو التي لديها مستوى واحد أعلى
    root_offices = Office.objects.filter(Q(parent__isnull=True) | Q(parent__parent__isnull=True))

    return render(request, 'accounts/employeesearch/mainemployeesearch.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
         'document_types': document_types, 
        'religions': religions,  # 🔹 إرسال قائمة الأديان إلى القالب
        'nationalisms': nationalisms,  # 🔹 إرسال قائمة القوميات إلى القالب # إرسال قائمة الوثائق إلى القالب
        'offices': root_offices,
        'course_certificates': course_certificates,
         'education_degrees': education_degrees,
         'employment_types': employment_types,
         'financial_allocations': financial_allocations,
         'position_type_query': position_type_query,
         'staff_structure_types': staff_structure_types,
         'placement_type_query': placement_type_query,
         'payroll_budget_types': payroll_budget_types,
         'punishment_types': punishment_types,
         'thanks_types': thanks_types,
         'absence_types': absence_types,
         
    })
