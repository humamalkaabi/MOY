from hrhub.models.hr_utilities_models import DutyAssignmentOrder
from hrhub.forms.hr_utitlity import Duty_Assignment_Order_Form
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from accounts.models import Employee
from django.contrib import messages
from unidecode import unidecode
from django.utils.text import slugify
from locations.models  import Governorate
import csv
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.utils.translation import gettext as _
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
@login_required
def main_duty_assignment_order(request):
    # التحقق من صلاحيات المستخدم
    # if not (request.user.has_perm('hrhub.view_duty_assignment_order') or
    #         request.user.has_perm('hrhub.add_duty_assignment_order') or
    #         request.user.has_perm('hrhub.change_duty_assignment_order') or
    #         request.user.has_perm('hrhub.delete_duty_assignment_order')):
    #     return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    duty_assignment_orders = DutyAssignmentOrder.objects.all()
    
    context = {
        'duty_assignment_orders': duty_assignment_orders
    }

    return render(request, 'hrhub/duty_assignment_order/main_duty_assignment_order.html', context)






@login_required
def add_duty_assignment_order(request):
    if not ( request.user.has_perm('hrhub.add_duty_assignment_order')):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    if request.method == 'POST':
        form = Duty_Assignment_Order_Form(request.POST)
        if form.is_valid():
            job_title = form.save(commit=False)
            job_title.created_by = request.user  # ربط بـ login user
            job_title.save()
            return redirect('hrhub:main_duty_assignment_order')  # يمكنك تعديل URL حسب الحاجة
    else:
        form = Duty_Assignment_Order_Form()
    return render(request, 'hrhub/duty_assignment_order/add_duty_assignment_order.html', {'form': form})



@login_required
def duty_assignment_order_detail(request, slug):
    # جلب العنوان الوظيفي المطلوب بناءً على slug
    duty_assignment_order = get_object_or_404(DutyAssignmentOrder, slug=slug)

    context = {
        'duty_assignment_order': duty_assignment_order
    }
    return render(request, 'hrhub/duty_assignment_order/duty_assignment_order_detail.html', context)



@login_required
def update_duty_assignment_order(request, slug):
    if not (request.user.has_perm('hrhub.change_duty_assignment_order')):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    duty_assignment_order = get_object_or_404(DutyAssignmentOrder, slug=slug)
    
    if request.method == 'POST':
        # تحديث البيانات باستخدام النموذج
        form = Duty_Assignment_Order_Form(request.POST, instance=duty_assignment_order)
        if form.is_valid():
            duty_assignment_order = form.save(commit=False)
            duty_assignment_order.created_by = request.user  # تحديث المستخدم الذي قام بالتعديل
            duty_assignment_order.save()
            messages.success(request, "تم تحديث العنوان الوظيفي بنجاح.")
            return redirect('hrhub:main_duty_assignment_order')  # تعديل المسار حسب الحاجة
    else:
        # عرض النموذج مع البيانات الحالية
        form = Duty_Assignment_Order_Form(instance=duty_assignment_order)
    
    context = {
        'form': form,
        'duty_assignment_order': duty_assignment_order
    }
    return render(request, 'hrhub/duty_assignment_order/update_duty_assignment_order.html', context)





@login_required
def delete_duty_assignment_order(request, slug):
    # التحقق من صلاحيات المستخدم
    if not request.user.has_perm('hrhub.delete_duty_assignment_order'):
        return HttpResponseForbidden("ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    
    # جلب سجل الديانة باستخدام الـ slug
    duty_assignment_order = get_object_or_404(DutyAssignmentOrder, slug=slug)
    
    # حذف السجل
    duty_assignment_order.delete()
    
    messages.success(request, "تم حذف هذه البيانات بنجاح.")
    return redirect('hrhub:main_duty_assignment_order')  # يمكنك تعديل الرابط بما يتناسب مع مشروعك


