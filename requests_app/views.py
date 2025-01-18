from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EmployeeRequest, RequestType
from .forms import EmployeeRequestForm
from personalinfo.models import BasicInfo
from django.shortcuts import render, get_object_or_404, redirect




@login_required
def create_employee_request(request, slug):
    requester = get_object_or_404(BasicInfo, slug=slug)

    if request.method == 'POST':
        form = EmployeeRequestForm(request.POST)
        if form.is_valid():
            employee_request = form.save(commit=False)
            employee_request.requester = requester  # تعيين الموظف مقدم الطلب
            employee_request.save()
            return redirect('accounts:view_profile')  # توجيه المستخدم إلى صفحة البروفايل بعد الحفظ
    else:
        form = EmployeeRequestForm()

    return render(request, 'requests_app/create_request.html', {'form': form, 'requester': requester})




from django.db.models import Q  # استيراد Q لاستخدامه في البحث المتعدد
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from hrhub.models.office_position_models import Office
from accounts.models import Employee

def mainrequests(request):
    username_query = request.GET.get('username', '')
    firstname_query = request.GET.get('firstname', '')
    secondname_query = request.GET.get('secondname', '')
    thirdname_query = request.GET.get('thirdname', '')
    has_basicinfo = request.GET.get('has_basicinfo', '')
    gender_query = request.GET.get('gender', '')
    has_phone = request.GET.get('has_phone', '')
    office_query = request.GET.get('office', '')  # استعلام الدائرة الجديدة
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

    # تصفية بناءً على الدائرة والدوائر المرتبطة
    if office_query:
        try:
            selected_office = Office.objects.get(id=office_query)
            related_offices = selected_office.get_descendants(include_self=True)
            query &= Q(basic_info__employee_offices__office__in=related_offices)
        except Office.DoesNotExist:
            pass

    employees = Employee.objects.filter(query).distinct()

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

    return render(request, 'requests_app/mainrequests.html', {
        'employees': page_obj,
        'employee_count': employees.count(),
        'results_per_page': results_per_page,
        'offices': root_offices,
    })


@login_required
def employee_requests_list(request, slug):
    # الحصول على الموظف باستخدام `slug`
    employee = get_object_or_404(BasicInfo, slug=slug)

    # جلب جميع الطلبات التي قدمها هذا الموظف
    requests = EmployeeRequest.objects.filter(requester=employee).order_by('-created_at')

    return render(request, 'requests_app/employee_requests_list.html', {'employee': employee, 'requests': requests})
