from django.shortcuts import render, redirect, get_object_or_404  # استيراد الدوال المستخدمة في معالجة الطلبات والردود.
from django.contrib.auth.decorators import login_required  # استيراد الديكوريتور للتحقق من أن المستخدم مسجل الدخول.
from django.http import HttpResponseForbidden, HttpResponse  # استيراد ردود HTTP للاستخدام في التحكم في الوصول والاستجابة.
from django.core.paginator import Paginator  # استيراد الكائن Paginator لتقسيم البيانات إلى صفحات.
from django.utils.dateparse import parse_date  # استيراد دالة parse_date لتحويل سلسلة نصية إلى كائن تاريخ.
import csv  # استيراد مكتبة CSV للتعامل مع ملفات CSV.
import logging  # استيراد مكتبة logging لتسجيل الرسائل والأخطاء.
from personalinfo.models import BasicInfo



logger = logging.getLogger(__name__)  # إنشاء كائن logger لتسجيل الرسائل مع اسم الوحدة الحالية.

# Create your views here.



@login_required
def main_control_panel(request):
    total_employees_count = Employee.objects.count()
    
    
    return render(request, 'accounts/main_control_panel.html', {
        'total_employees_count': total_employees_count,
       
    })



@login_required
def main_accounts_page(request):
    
    
    return render(request, 'accounts/main_accounts_page.html', {
       
    })




from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

User = get_user_model()

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"http://yourdomain.com/reset/{uid}/{token}/"

        send_mail(
            "إعادة تعيين كلمة المرور",
            f"لإعادة تعيين كلمة المرور، اضغط على الرابط التالي: {reset_link}",
            "your-email@gmail.com",
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني."}, status=status.HTTP_200_OK)

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, user.DoesNotExist):
            return Response({"error": "الرابط غير صالح"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            new_password = request.data.get("password")
            user.set_password(new_password)
            user.save()
            return Response({"message": "تم تغيير كلمة المرور بنجاح"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "الرابط غير صالح أو منتهي"}, status=status.HTTP_400_BAD_REQUEST)




from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from .forms import PasswordResetByEmployeeIDForm
from .models import Employee
from django.utils.translation import gettext_lazy as _


from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import PasswordResetView
from .forms import PasswordResetByEmployeeIDForm
from .models import Employee
from personalinfo.models import BasicInfo
from django.views.generic.edit import FormView


class CustomPasswordResetView(FormView):
    template_name = 'registration/password_reset_by_employee_id.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetByEmployeeIDForm

    def form_valid(self, form):
        employee_id = form.cleaned_data['employee_id']
        try:
            employee = Employee.objects.get(username=employee_id)
            if hasattr(employee, 'basic_info') and employee.basic_info.email:
                email = employee.basic_info.email
                current_site = get_current_site(self.request)
                subject = _("إعادة تعيين كلمة المرور")
                message = render_to_string('registration/password_reset_email.html', {
                    'user': employee,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(employee.pk)),
                    'token': default_token_generator.make_token(employee),
                    'protocol': 'https' if self.request.is_secure() else 'http',
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Employee.DoesNotExist:
            pass  # لأغراض الأمان، لا تفصح عن وجود أو عدم وجود المستخدم

        return super().form_valid(form)
    

from django.contrib.auth.views import PasswordResetConfirmView

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
