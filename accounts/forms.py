from django import forms
from django.contrib.auth.models import Permission
from django.forms import ModelForm
from collections import defaultdict
from .models import Employee
from django import forms
from django.contrib.auth.models import Permission
from django.apps import apps
from collections import defaultdict
from django.contrib.auth.forms import UserCreationForm

class EmployeePermissionForm(forms.ModelForm):
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="الصلاحيات"
    )

    class Meta:
        model = Employee
        fields = ['user_permissions']


class BulkPermissionForm(forms.Form):
    # تصفية الصلاحيات لاستبعاد الافتراضية (add, change, delete, view)
    filtered_permissions = Permission.objects.exclude(
        codename__startswith=('add_', 'change_', 'delete_', 'view_')
    ).select_related('content_type')

    permissions = forms.ModelMultipleChoiceField(
        queryset=filtered_permissions,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="اختر الصلاحيات"
    )


class BulkRevokePermissionForm(forms.Form):
    # تصفية الصلاحيات لاستبعاد الافتراضية (add, change, delete, view)
    filtered_permissions = Permission.objects.exclude(
        codename__startswith=('add_', 'change_', 'delete_', 'view_')
    ).select_related('content_type')

    permissions = forms.ModelMultipleChoiceField(
        queryset=filtered_permissions,
        widget=forms.CheckboxSelectMultiple,
        required=False,  # جعل الحقل غير مطلوب حتى يمكن تقديم الطلب بدون تحديد صلاحيات
        label="اختر الصلاحيات لسحبها"
    )




######################################### Registration #################################

# تعريف نموذج تسجيل الموظف الجديد الذي يرث من UserCreationForm.
class EmployeeRegistrationForm(UserCreationForm):
    class Meta:  # تعريف إعدادات النموذج الداخلية.
        model = Employee  # تعيين النموذج المستخدم لهذا النموذج إلى Employee.
        fields = ['username', 'password1', 'password2']  # تحديد الحقول التي سيتم عرضها في النموذج.
        labels = {  # تعيين تسميات مخصصة للحقول لعرضها في واجهة المستخدم.
            'username': 'رقم وظيفي',  # تسمية حقل "username" بـ "رقم وظيفي".
            'password1': 'كلمة المرور',  # تسمية حقل "password1" بـ "كلمة المرور".
            'password2': 'تأكيد كلمة المرور',  # تسمية حقل "password2" بـ "تأكيد كلمة المرور".
        }

# نموذج لتحميل ملفات CSV للموظفين.
class CSVUploadEmployeesForm(forms.Form):
    csv_file = forms.FileField(label="رجاءا قم برفع ملف CSV")  # حقل لتحميل ملف CSV مع تسمية مخصصة.





############### Old########


from django import forms  # استيراد مكتبة forms لإنشاء النماذج في Django.
from django.contrib.auth.forms import UserCreationForm  # استيراد النموذج الأساسي لإنشاء المستخدمين (UserCreationForm) من مكتبة المصادقة.
from .models import Employee  # استيراد نموذج Employee من ملفات النماذج الخاصة بالمشروع.
from django.contrib.auth.models import Permission, Group  # استيراد نموذج Permission لإدارة الصلاحيات.

# تعريف نموذج تسجيل الموظف الجديد الذي يرث من UserCreationForm.
class EmployeeRegistrationForm(UserCreationForm):
    class Meta:  # تعريف إعدادات النموذج الداخلية.
        model = Employee  # تعيين النموذج المستخدم لهذا النموذج إلى Employee.
        fields = ['username', 'password1', 'password2']  # تحديد الحقول التي سيتم عرضها في النموذج.
        labels = {  # تعيين تسميات مخصصة للحقول لعرضها في واجهة المستخدم.
            'username': 'رقم وظيفي',  # تسمية حقل "username" بـ "رقم وظيفي".
            'password1': 'كلمة المرور',  # تسمية حقل "password1" بـ "كلمة المرور".
            'password2': 'تأكيد كلمة المرور',  # تسمية حقل "password2" بـ "تأكيد كلمة المرور".
        }

# نموذج لتحميل ملفات CSV للموظفين.
class CSVUploadEmployeesForm(forms.Form):
    csv_file = forms.FileField(label="رجاءا قم برفع ملف CSV")  # حقل لتحميل ملف CSV مع تسمية مخصصة.


# forms.py
from django import forms
from django.contrib.auth.models import Permission
from .models import Employee

class AssignPermissionsForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        label="الموظف",
        empty_label="اختر الموظف"
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="الصلاحيات"
    )
    select_all = forms.BooleanField(required=False, label="اختيار جميع الموظفين")

class GroupPermissionForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Permissions'  # Adding label to the permissions field
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'اسم المجموعة',  # Adding label to the name field
        }



class AddEmployeesToGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )


from django import forms
from django.contrib.auth.forms import SetPasswordForm

class CustomSetPasswordForm(SetPasswordForm):
    class Meta:
        model = Employee  # استبدل بـ النموذج الخاص بك إذا كان مختلفًا
        fields = ('new_password1', 'new_password2')




class EmployeeSearchForm(forms.Form):
    username = forms.CharField(
        max_length=15,
        label="رقم الموظف",
        widget=forms.TextInput(attrs={'placeholder': 'أدخل رقم الموظف'})
    )



class EmployeeApprovalForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['is_approved']  # أو إضافة الحقول الأخرى التي ترغب في تعديلها

    # في حالة كان لديك أي تخصيصات أخرى تحتاجها
    is_approved = forms.BooleanField(required=False, label="هل تريد تفعيل او الغاء تفعيل الحساب")





from django import forms
from .models import Employee
from django.utils.translation import gettext_lazy as _

class PasswordResetByEmployeeIDForm(forms.Form):
    employee_id = forms.CharField(
        max_length=15,
        label=_("الرقم الوظيفي"),
        help_text=_("أدخل رقمك الوظيفي لإعادة تعيين كلمة المرور.")
    )

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get("employee_id")
        try:
            employee = Employee.objects.get(username=employee_id)
            if not hasattr(employee, 'basic_info') or not employee.basic_info.email:
                raise forms.ValidationError(_("لم يتم العثور على بريد إلكتروني مرتبط بهذا الرقم الوظيفي."))
        except Employee.DoesNotExist:
            raise forms.ValidationError(_("لم يتم العثور على موظف بهذا الرقم الوظيفي."))
        return employee_id