
from django import forms
from hrhub.models.employee_leave_models import LeaveType, LeaveBalance, LeaveRequest


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'is_balance_based', 'accepts_negative_numbers', 'max_days_per_year', 'monthly_increment', 'accepts_negative_numbers',  'leave_paid_type', 'leave_type_document', 'comments']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الإجازة'}),
            'is_balance_based': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accepts_negative_numbers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_days_per_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'الحد الأقصى من الأيام سنويًا'}),
            'monthly_increment': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'الزيادة الشهرية'}),
        }




class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'status']  # إزالة `employee` لأننا سنمرره من `slug`
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'leave_type': 'نوع الإجازة',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'status': 'الحالة',
        }



class LeaveBalanceForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = ['old_balance',  'leave_type', 'start_date']
        
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
           
        }  # لا تحتاج إلى employee هنا








class LeaveBalanceCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي علي بيانات الموظفين منن رصيد الاجازات    .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )


class LeaveRequestCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي علي بيانات الموظفين من الاجازات    .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )



    