from django import forms
from hrhub.models.employement_models import EmployementType, EmploymentHistory

class EmployementTypeForm(forms.ModelForm):
    class Meta:
        model = EmployementType
        fields = ['name', 'is_default', 'is_employment_type_counted', 'pdf_file', 'comments']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم نوع التوظيف'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_employment_type_counted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'أدخل الملاحظات'}),
        }


# class EmployementTypeForm(forms.ModelForm):
#     class Meta:
#         model = EmployementType
#         fields = ['name', 'is_employement_type_counted', 'pdf_file', 'comments']
#         widgets = {
#             'comments': forms.Textarea(attrs={'rows': 4}),
#             'is_employement_type_counted': forms.CheckboxInput(attrs={'class': 'custom-checkbox', 'id': 'is_employement_type_counted_id'}),
#         }


# from hrhub.models.employement_models import EmploymentHistory, EmployementType

class EmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = EmploymentHistory
        fields = ['start_date', 'end_date', 'employee_duration_year', 'employee_duration_month', 'employee_duration_day',
                  'employee_type', 'employee_place', 'pdf_file', 'comments']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }