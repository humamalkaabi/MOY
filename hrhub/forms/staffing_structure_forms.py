from django import forms
from hrhub.models.staffing_structure_models import PayrollBudgetType, StaffStructerType, EmployeeStaffKind




class PayrollBudgetTypeForm(forms.ModelForm):
    class Meta:
        model = PayrollBudgetType
        fields = ['name_in_arabic', 'name_in_english', 'is_default', 'commennts']
        labels = {
            'name_in_arabic': 'الاسم بالعربية',
            'name_in_english': 'الاسم بالإنجليزية',
            'is_default': 'افتراضي',
            'commennts': 'ملاحظات'
        }


class StaffStructerTypeForm(forms.ModelForm):
    class Meta:
        model = StaffStructerType
        fields = ['name_in_arabic', 'name_in_english', 'payroll_budget_type', 'is_default', 'commennts']
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم نوع الملاك بالعربية'}),
            'name_in_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم نوع الملاك بالإنجليزية'}),
            'payroll_budget_type': forms.Select(attrs={'class': 'form-control'}),
            'commennts': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'أدخل ملاحظات'}),
        }



class EmployeeStaffKindForm(forms.ModelForm):
    class Meta:
        model = EmployeeStaffKind
        fields = [
            'employee_staff_type', 
            'employee_staff_type_number',
            'employee_staff_type_number_date', 
            'pdf_file', 
            'comments'
        ]
        widgets = {
            'employee_staff_type_number_date': forms.DateInput(attrs={'type': 'date'}),
        }








class EmployeeStaffKindCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات الملاك للموظفين .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )