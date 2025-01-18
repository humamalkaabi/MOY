import csv  # استيراد مكتبة csv للتعامل مع ملفات CSV (قراءة/كتابة).

from django.shortcuts import render, redirect, get_object_or_404  # استيراد دوال render (لإظهار الصفحات)، وredirect (لإعادة التوجيه)، وget_object_or_404 (لإحضار كائن أو عرض خطأ 404 إذا لم يكن موجودًا).
from django.contrib.auth.decorators import login_required, permission_required  # استيراد ديكوراتور login_required للتحقق من تسجيل الدخول، وpermission_required للتحقق من صلاحيات معينة.
from django.http import HttpResponse, HttpResponseForbidden  # استيراد HttpResponse لإرجاع استجابة عادية، وHttpResponseForbidden لإرجاع استجابة بمنع الوصول (403).
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate  # استيراد دوال تسجيل الدخول، وتسجيل الخروج، والتحقق من المستخدم (authenticate).
from django.contrib.auth.views import PasswordChangeView  # استيراد PasswordChangeView لتغيير كلمة المرور.
from django.contrib.auth.forms import AuthenticationForm  # استيراد نموذج تسجيل الدخول الافتراضي (AuthenticationForm) من Django.
from django.contrib import messages  # استيراد messages لإضافة رسائل موجهة للمستخدم مثل النجاح أو الخطأ.
from django.utils import translation  # استيراد translation لتغيير لغة العرض (التدويل).
from django.core.exceptions import ValidationError  # استيراد ValidationError لرفع استثناء عند حدوث أخطاء في التحقق من البيانات.
from django.template.loader import render_to_string  # استيراد render_to_string لتحويل قالب HTML إلى نص باستخدام المتغيرات.
from django.core.mail import send_mail  # استيراد send_mail لإرسال رسائل البريد الإلكتروني.
from django.conf import settings  # استيراد settings للوصول إلى إعدادات المشروع (مثل إعدادات البريد الإلكتروني).
from django.contrib.auth.tokens import default_token_generator  # استيراد default_token_generator لإنشاء الرموز (tokens) الخاصة بتأكيد البريد الإلكتروني أو استعادة كلمة المرور.
from django.utils.http import urlsafe_base64_encode  # استيراد urlsafe_base64_encode لترميز بيانات المستخدم بشكل آمن للاستخدام في الروابط.
from django.utils.encoding import force_bytes  # استيراد force_bytes لتحويل البيانات إلى بايتات، غالبًا للاستخدام في الرموز (tokens).

from .forms import EmployeeRegistrationForm, CSVUploadEmployeesForm  # استيراد النماذج الخاصة بتسجيل الموظفين وتحميل ملفات CSV.
from .models import Employee  # استيراد نموذج Employee الخاص بالموظفين.
from django.contrib.auth.hashers import make_password  # استيراد make_password لتجزئة كلمات المرور قبل حفظها في قاعدة البيانات.
from personalinfo.models import BasicInfo
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth import login, authenticate

def register_new_employee(request):  # دالة لتسجيل موظف جديد.
    # Activate Arabic language
    translation.activate('ar')  # تفعيل اللغة العربية للواجهة.

    # Get the currently logged-in employee
    employee_login = get_object_or_404(Employee, username=request.user.username)  # الحصول على كائن الموظف الحالي بناءً على اسم المستخدم.

    if request.method == 'POST':  # التحقق مما إذا كان الطلب من النوع POST (أي إرسال بيانات النموذج).
        form = EmployeeRegistrationForm(request.POST)  # إنشاء نموذج تسجيل الموظف الجديد ببيانات POST.
        if form.is_valid():  # التحقق مما إذا كانت البيانات المرسلة صالحة.
            employee = form.save(commit=False)  # حفظ الموظف الجديد دون حفظه فعليًا في قاعدة البيانات حتى الآن.
            
            # Set the creator of the employee
            employee.created_by = employee_login  # تعيين الموظف الذي قام بإنشاء هذا الحساب.
            employee.is_approved = True  # تعيين حالة اعتماد الموظف الجديد كمعتمد.

            employee.save()  # حفظ الموظف الجديد في قاعدة البيانات.
            # print(f"Redirecting to employee slug: {employee.slug}")  # Debugging print statement
            messages.success(request, 'تم التسجيل بنجاح!')  # إرسال رسالة نجاح للمستخدم.
            return redirect('accounts:employeedashboard', slug=employee.slug)  # إعادة التوجيه بعد التسجيل إلى تفاصيل الموظف الجديد.
        else:
            messages.error(request, 'رجاءا صحح الاخطاء.')  # عرض رسالة خطأ إذا كانت البيانات غير صالحة.
    else:
        form = EmployeeRegistrationForm()  # إذا كان الطلب من النوع GET، يتم عرض نموذج فارغ.

    return render(request, 'accounts/registration/register_new_employee.html', {'form': form})  # عرض صفحة التسجيل مع النموذج.




@login_required  # التحقق من أن المستخدم قام بتسجيل الدخول قبل الوصول إلى هذه الدالة.
def upload_employees_csv(request):  # دالة لتحميل الموظفين من ملف CSV.
    employee_login = get_object_or_404(Employee, username=request.user.username)  # الحصول على كائن الموظف الذي قام بتسجيل الدخول.

    # Check if the user has permission to upload employees
    if not request.user.is_superuser:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        return redirect('accounts:view_profile')   # عرض رسالة خطأ إذا لم يكن لديه الصلاحية.

    if request.method == 'POST':  # التحقق مما إذا كان الطلب من النوع POST (إرسال بيانات).
        form = CSVUploadEmployeesForm(request.POST, request.FILES)  # تهيئة نموذج رفع ملف CSV.
        if form.is_valid():  # التحقق من صحة النموذج المرسل.
            csv_file = request.FILES['csv_file']  # الحصول على ملف CSV المرفوع.
            decoded_file = csv_file.read().decode('utf-8').splitlines()  # قراءة محتويات الملف وفك ترميزه إلى نص.
            reader = csv.reader(decoded_file)  # تهيئة قارئ CSV.
            next(reader)  # تجاوز صف العنوان (إذا كان موجودًا).

            errors = []  # قائمة لحفظ الأخطاء المحتملة.
            success_count = 0  # عداد لعدد الموظفين الذين تم تحميلهم بنجاح.

            for row in reader:  # حلقة لمعالجة كل صف في ملف CSV.
                if len(row) != 2:  # التحقق من صحة تنسيق الصف.
                    errors.append(f"Invalid row format: {row}")  # إذا كان التنسيق غير صحيح، إضافة رسالة خطأ.
                    continue  # الانتقال إلى الصف التالي.

                username, password = row  # الحصول على اسم المستخدم وكلمة المرور من الصف.
                employee_data = {
                    'username': username,  # تعيين اسم المستخدم.
                    'password': make_password(password),  # تشفير كلمة المرور باستخدام make_password.
                }

                try:
                    # Validate data and create employee
                    employee = Employee(**employee_data)  # إنشاء كائن موظف جديد مع البيانات.
                    employee.full_clean()  # التحقق من صحة بيانات الموظف (validation).
                    employee.save()  # حفظ الموظف في قاعدة البيانات.
                    success_count += 1  # زيادة عداد الموظفين الناجحين.
                except ValidationError as ve:  # إذا كان هناك خطأ في التحقق من صحة البيانات.
                    errors.append(f"Validation error for employee {username}: {ve.message_dict}")  # إضافة رسالة الخطأ.
                except Exception as e:  # التعامل مع أي خطأ آخر.
                    errors.append(f"Error saving employee {username}: {str(e)}")  # إضافة رسالة خطأ.

            if errors:  # إذا كانت هناك أخطاء.
                messages.error(request, f"Errors occurred: {', '.join(errors)}")  # عرض رسالة خطأ.
                return render(request, 'accounts/registration/upload_employees_csv.html', {'form': form, 'errors': errors})  # إعادة عرض النموذج مع الأخطاء.

            messages.success(request, f"Successfully uploaded {success_count} employees!")  # عرض رسالة نجاح إذا تم رفع الموظفين بنجاح.
            return redirect('personalinfo:mainbasicinfo')  # إعادة التوجيه بعد نجاح الرفع.

    else:
        form = CSVUploadEmployeesForm()  # عرض نموذج فارغ إذا كان الطلب GET.

    return render(request, 'accounts/registration/upload_employees_csv.html', {'form': form})  # عرض صفحة تحميل CSV مع النموذج.

@login_required 
def generate_sample_upload_employees_csv_csv(request):  # دالة لإنشاء ملف CSV يحتوي على بيانات موظفين نموذجية.
    
    employee_login = get_object_or_404(Employee, username=request.user.username)  # الحصول على كائن الموظف الذي قام بتسجيل الدخول.

    # Check if the user has permission to upload employees
    # if not employee_login.has_register_employee_permission(request.user):  # التحقق مما إذا كان الموظف الحالي لديه صلاحية تحميل موظفين.
    #     return HttpResponseForbidden("ليس لديك الصلاحيات اللازمة لتسجيل موظف جديد.")  # عرض رسالة خطأ إذا لم يكن لديه الصلا
    
    # Sample employee data
    employees = [
        {'username': '78000000000', 'password': 'password123'},  # بيانات الموظف النموذجية: اسم المستخدم وكلمة المرور.
    ]
    
    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')  # تهيئة استجابة HTTP مع محتوى من نوع CSV.
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'  # تحديد أن الاستجابة ستُرسل كملف مرفق باسم "employees.csv".
    
    writer = csv.writer(response)  # إنشاء كاتب CSV لإضافة البيانات إلى الاستجابة.
    
    # Write the header
    writer.writerow(['username', 'password'])  # كتابة العناوين (الرأس) لملف CSV.

    # Write employee data
    for employee in employees:  # حلقة لكتابة بيانات كل موظف.
        writer.writerow([employee['username'], employee['password']])  # كتابة بيانات كل موظف في صف خاص به في ملف CSV.

    return response  # إرجاع الاستجابة التي تحتوي على ملف CSV ليتم تنزيلها من قبل المستخدم.



from core.models import Logo 


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, "الحساب غير معتمد. الرجاء التواصل مع الإدارة.")
                    return redirect("accounts:account_disabled")  # إعادة التوجيه إلى صفحة الحساب المعطل
                
                # تسجيل الدخول للمستخدم
                login(request, user)

                # التحقق من إذا كان المستخدم يقوم بتسجيل الدخول لأول مرة
                if user.is_first_login:
                    return redirect("accounts:password_change")  # إعادة التوجيه لتغيير كلمة المرور

                # التحقق من إذا كان للمستخدم معلومات أساسية مرتبطة
                try:
                    basic_info = BasicInfo.objects.get(emp_id=user)
                except BasicInfo.DoesNotExist:
                    # إذا لم يكن هناك معلومات أساسية، إعادة التوجيه لإنشاء أو تعديل المعلومات الأساسية
                    return redirect("accounts:view_profile")

                # إذا كان لديه معلومات أساسية، إعادة التوجيه إلى الملف الشخصي
                return redirect("accounts:view_profile")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    logo = Logo.objects.first()

    return render(request, "accounts/registration/login_view.html", {"form": form, "logo": logo})


def account_disabled(request):
    
    return render(request, "accounts/account_disabled.html")



# from django.shortcuts import redirect
# from django.contrib.auth.views import PasswordChangeView
# from django.contrib import messages

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/registration/password_change_form.html'

    def form_valid(self, form):
        # تغيير كلمة المرور
        response = super().form_valid(form)
        user = self.request.user

        # تعيين is_first_login إلى False بعد تغيير كلمة المرور
        user.is_first_login = False
        user.save()

        messages.success(self.request, 'تم تغيير كلمة المرور بنجاح!')

        # التحقق مما إذا كان لدى المستخدم معلومات أساسية
        basicinfo = getattr(user, 'basicinfo', None)
        if basicinfo is not None:
            return redirect("basicinfo:create_or_update_basic_info_himself")
            
        else:
            return redirect("accounts:view_profile")





@login_required
def logout_view(request):
    # Activate Arabic language
    translation.activate('ar')
    auth_logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح!')
    return redirect('accounts:login_view')

