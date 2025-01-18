from django import forms
from hrhub.models.thanks_punishment_absence_models import EmployeeThanks, ThanksType
from personalinfo.models import BasicInfo

class ThanksTypeForm(forms.ModelForm):
    class Meta:
        model = ThanksType
        fields = ['thanks_name', 'thanks_impact', 'comments']
        labels = {
            'thanks_name': 'اسم الشكر',
            'thanks_impact': 'تأثير الشكر',
            'comments': 'ملاحظات',
        }
        widgets = {
            'thanks_name': forms.TextInput(attrs={'class': 'form-control'}),
            'thanks_impact': forms.NumberInput(attrs={'class': 'form-control'}),
            'comments': forms.TextInput(attrs={'class': 'form-control'}),
        }

        


class EmployeeThanksOneForm(forms.ModelForm):
    class Meta:
        fields = ['thanks_type', 'thanks_number', 'date_issued', 'is_counted', 'approved', 'comments']
        model = EmployeeThanks
        labels = {
            'thanks_name': 'اسم نوع الشكر',
            'thanks_number': 'رقم كتاب الشكر',
            'date_issued': 'تاريخ احتسابه',
        }
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }



class EmployeeThanksCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="يرجى تحميل ملف بصيغة CSV يحتوي على بيانات كتب الشكر للموظفين."
    )

from hrhub.models.thanks_punishment_absence_models import EmployeePunishment, PunishmentType
class EmployeePunishmentForm(forms.ModelForm):
    emp_id_punishment = forms.ModelMultipleChoiceField(
        queryset=BasicInfo.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="الموظفون",
        help_text="اختر الموظفين الذين سيتم معاقبتهم."
    )

    class Meta:
        model = EmployeePunishment
        fields = ['punishment_type', 'punishment_number', 'date_issued', 'is_counted', 'approved', 'comments', 'emp_id_punishment']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }


class PunishmentTypeForm(forms.ModelForm):
    class Meta:
        model = PunishmentType
        fields = ['punishment_name', 'punishment_impact', 'comments']
        widgets = {
            'punishment_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العقوبة'}),
            'punishment_impact': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'تأثير العقوبة'}),
            'comments': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ملاحظات إضافية'}),
        }

class EmployeePunishmentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات كتب العقوبات.",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )


class EmploymentHistoryCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات خدمات الموظف .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )





class EmployeeAbsenceCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات كتب الغياب.",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )

############## Count

class UpdateThanksCountedForm(forms.ModelForm):
    class Meta:
        model = EmployeeThanks
        fields = ['is_counted']  # تضمين الحقل الذي نريد تعديله



class UpdatePunishmentsCountedForm(forms.ModelForm):
    class Meta:
        model = EmployeePunishment
        fields = ['is_counted']


class UpdateDateIssuedForm(forms.ModelForm):
    class Meta:
        model = EmployeeThanks
        fields = ['date_issued']  # الحقل الذي سيتم تحديثه فقط
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'date_issued': 'تاريخ إصدار كتاب الشكر',
        }


############################
from hrhub.models.thanks_punishment_absence_models import AbsenceType, EmployeeAbsence

class AbsenceTypeForm(forms.ModelForm):
    class Meta:
        model = AbsenceType
        fields = ['absence_name', 'absence_impact', 'comments']
        labels = {
            'absence_name': 'اسم الغياب',
            'absence_impact': 'تأثير الغياب',
            'comments': 'تفاصيل إضافية',
        }
        widgets = {
            'absence_name': forms.TextInput(attrs={'class': 'form-control'}),
            'absence_impact': forms.NumberInput(attrs={'class': 'form-control'}),
            'comments': forms.TextInput(attrs={'class': 'form-control'}),
        }



class EmployeeAbsenceForm(forms.ModelForm):
    class Meta:
        model = EmployeeAbsence
        fields = ['absence_type', 'absence_number', 'date_issued', 'start_date', 'end_date', 'duration_years', 'duration_months', 'duration_days','comments']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
        }





class EmployeeThanksForm(forms.ModelForm):
    class Meta:
        model = EmployeeThanks
        fields = ['thanks_type', 'thanks_number', 'date_issued', 'pdf_file', 'is_counted', 'approved', 'comments']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
        }


class EmployeePunishmentForm(forms.ModelForm):
    class Meta:
        model = EmployeePunishment
        fields = ['punishment_type', 'punishment_number', 'date_issued', 'pdf_file', 'is_counted', 'approved', 'comments']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
        }



class UpdateIsCountedForm(forms.ModelForm):
    class Meta:
        model = EmployeePunishment
        fields = ['is_counted']
        widgets = {
            'is_counted': forms.Select(choices=EmployeePunishment.COUNT_CHOICES, attrs={'class': 'form-control'}),
        }
        labels = {
            'is_counted': 'يتم احتسابه',
        }


from accounts.models import Employee
class EmployeeSelectionForm(forms.Form):
    selected_employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="اختيار الموظفين"
    )
