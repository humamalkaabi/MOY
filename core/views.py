from django.shortcuts import render

# Create your views here.

def sucess_link(request):

   

    return render(request, 'core/sucess_link.html')


# core/views.py

from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect


def custom_403(request, exception=None):
    # إرسال رسالة خطأ إلى المستخدم
    messages.error(request, "عذرًا، ليس لديك الصلاحية للوصول إلى هذه الصفحة.")
    # إعادة التوجيه إلى الصفحة الرئيسية أو صفحة مخصصة
    return redirect('accounts:view_profile')  # استبدل 'home' باسم الصفحة التي تريد إعادة التوجيه إليها


from django.shortcuts import render
from accounts.registration import login_view
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import Main_About_US, Logo
from .forms import MainAboutUsForm, LogoForm
from django.utils import timezone

# Create your views here.


def main_page(request):
    # Call the employee_login_view function
    response = login_view(request)

    # Return the response from employee_login_view
    return response

@login_required
def create_or_update_main_about_us(request):

    if not request.user.has_perm('core.can_create_main_about_us'):
        return redirect('accounts:view_profile')  # التوجيه إلى صفحة البروفايل


    # محاولة جلب السجل الأول إذا كان موجودًا، إذا لم يكن موجودًا سيتم إنشاءه لاحقًا
    main_about_us = Main_About_US.objects.first()

    if request.method == 'POST':
        form = MainAboutUsForm(request.POST, instance=main_about_us)
        if form.is_valid():
            if not main_about_us:
                # إذا لم يكن هناك سجل، نقوم بإنشاءه
                form.instance.created_by = request.user  # تعيين المستخدم الذي أنشأ السجل
            else:
                # إذا كان السجل موجودًا، نقوم بتحديث حقل `updated_at`
                form.instance.updated_at = timezone.now()
            
            form.save()
            return redirect('core:view_main_about_us')  # التوجيه إلى صفحة التحديث
    else:
        form = MainAboutUsForm(instance=main_about_us)

    return render(request, 'core/contactus/main_about_us_form.html', {'form': form})



def view_main_about_us(request):
    # جلب أول سجل من Main_About_US
    main_about_us = Main_About_US.objects.first()
    logo = Logo.objects.order_by('-id').first()

    # إذا لم يكن هناك سجل، يمكنك توجيه المستخدم إلى صفحة أخرى أو إظهار رسالة
    if not main_about_us:
        return HttpResponse("لا يوجد بيانات للعرض.")
    
    return render(request, 'core/contactus/view_main_about_us.html', {'main_about_us': main_about_us,
                                                                      'logo': logo})


def logo_view(request):
    # جلب أول شعار من قاعدة البيانات (يفترض أن يوجد شعار واحد فقط)
    logo = Logo.objects.first()
    
    # عرض الشعار في القالب
    return render(request, 'core/logo/logo_view.html', {'logo': logo})


def logo_context(request):
    """
    إرجاع الشعار ليكون متاحًا في جميع القوالب.
    """
    logo = Logo.objects.first()
    return {"logo": logo}


@login_required
def create_or_update_logo(request):
    if not request.user.has_perm('core.can_create_main_about_us'):
        return redirect('accounts:view_profile')  # التوجيه إلى صفحة البروفايل


    logo = Logo.objects.first()  # محاولة جلب أول سجل

    if request.method == 'POST':
        form = LogoForm(request.POST, request.FILES, instance=logo)  # تأكد من إضافة request.FILES هنا
        if form.is_valid():
            if not logo:
                form.instance.created_by = request.user  # تعيين المستخدم
            else:
                form.instance.updated_at = timezone.now()  # تحديث حقل `updated_at`

            form.save()  # حفظ النموذج
            return redirect('core:logo_view')  # التوجيه إلى صفحة عرض الشعار بعد التحديث
    else:
        form = LogoForm(instance=logo)

    return render(request, 'core/logo/logo_form.html', {'form': form})


