from django import forms
from rddepartment.models.course_certificate_models import CourseCertificateType, CourseCertificateInstitution




class CourseCertificateTypeForm(forms.ModelForm):
    class Meta:
        model = CourseCertificateType
        fields = [
            'name_in_arabic', 
            'name_in_english', 
            'is_approved', 
            
        ]
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control'}),
            'name_in_english': forms.TextInput(attrs={'class': 'form-control'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # إضافة widget لحقل is_approved

            
           
        

        }


class CourseCertificateInstitutionForm(forms.ModelForm):
    class Meta:
        model = CourseCertificateInstitution
        fields = [
            'is_default',
            'name_in_arabic',
            'name_in_english',
            'comments',
        ]
        widgets = {
           
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل الاسم بالعربية'}),
            'name_in_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل الاسم بالإنجليزية'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'أدخل الملاحظات'}),
        }





from django import forms
from rddepartment.models.course_certificate_models import EmployeeCourseCertificate

class EmployeeCourseCertificateForm(forms.ModelForm):
    class Meta:
        model = EmployeeCourseCertificate
        fields = [
            'coursecertificatetype', 'name_of_the_institution', 'course_number',
            'date_issued', 'start_date', 'end_date', 'certificate_file', 'course_duration', 'comments'
        ]
        widgets = {
           
            'coursecertificatetype': forms.Select(attrs={'class': 'form-control'}),
            'name_of_the_institution': forms.Select(attrs={'class': 'form-control'}),
            'course_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'certificate_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'course_duration': forms.TextInput(attrs={'class': 'form-control'}),
             'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'أدخل الملاحظات'}),
        }




from django import forms

class EmployeeCourseCertificateCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات الشهادات التدريبية."
    )
