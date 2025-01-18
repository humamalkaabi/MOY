from django import forms
from hrhub.models.employee_job_title_models import JobTitle, EmployeeJobTitle, EmployeeJobTitleSettings

from django import forms

from django.core.exceptions import ValidationError


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = ['title_in_arabic', 'parent', 'description']
        widgets = {
            'title_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان وظيفي'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'وصف الوظيفة'}),
        }

# forms.py
class EmployeeJobTitleSettingsForm(forms.ModelForm):
    class Meta:
        model = EmployeeJobTitleSettings
        fields = ['auto_EmployeeJobTitle_upgrade', 'future_EmployeeJobTitle_upgrade']
        labels = {
            'auto_EmployeeJobTitle_upgrade': "حساب العنوان الوظيفي الحالي تلقائياً",
            'future_EmployeeJobTitle_upgrade': "حساب العنوان الوظيفي القادم تلقائياً"
        }
        widgets = {
            'auto_EmployeeJobTitle_upgrade': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'future_EmployeeJobTitle_upgrade': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# forms.py

from django import forms

class EmployeeJobTitleForm(forms.ModelForm):
    parent_job_title = forms.ModelChoiceField(
        queryset=JobTitle.objects.filter(parent__isnull=True),  # فقط العناوين الوظيفية من المستوى الأعلى
        required=False,
        label=("العنوان الوظيفي الأعلى")
    )

    class Meta:
        model = EmployeeJobTitle
        fields = ['auto_Employeee_upgrade', 'parent_job_title', 'start_employee_job_title',
                  'employee_job_title', 'next_employee_job_title', 
                  'start_employee_job_title_date', 'employee_job_title_date', 'next_employee_job_title_date',
                  'comments', 'created_by', 'is_approved']
        widgets = {
            'start_employee_job_title_date': forms.DateInput(attrs={'type': 'date'}),
            'employee_job_title_date': forms.DateInput(attrs={'type': 'date'}),
            'next_employee_job_title_date': forms.DateInput(attrs={'type': 'date'}),
        }




class EmployeeJobTitleCSVUploadForm(forms.Form):
    csv_file = forms.FileField()

# class EmployeeJobTitleForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeJobTitle
#         fields = [ 'employee_job_title', 'employee_job_title_date', 'job_title_number', 
#                   'job_title_file', 'next_employee_job_title', 'comments', 
#                   'is_approved']
        
#         widgets = {
#             'employee_job_title_date': forms.DateInput(attrs={'type': 'date'}),
#        


class JobTitleCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات العناوين الوظيفية."
    )


class EmployeeJobTitleCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات العناوين الوظيفية."
    )


    