from django import forms
from rddepartment.models.employee_education_models import EmployeeEducation



# class EmployeeEducationForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeEducation
#         fields = [
#             'education_degree_type', 'Certificate_Type', 'certificat_minstery_type', 'institution_name', 'iraqi_university', 
#             'foreign_university', 'college',  'certificate_file', 'effective_time', 
#             'date_of_administrative_order', 'duty_assignment_number','date_issued', 'date_of_enrollment', 'graduation_date'
#         ]
#         widgets = {
#             'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'effective_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'date_of_administrative_order': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'date_of_enrollment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'graduation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#         }




class EmployeeEducationForm(forms.ModelForm):
    class Meta:
        model = EmployeeEducation
        fields = [
            'education_degree_type',
            'certificat_minstery_type',
            'institution_name',
            'university_Type',
            'iraqi_university',
            'foreign_university',
            'college',
            'Certificate_Type',
            'date_issued',
            'duty_assignment_order',
            'duty_assignment_number', 
            'date_of_administrative_order',
            'date_of_enrollment',
            'graduation_date',
            'certificate_file', 
            'effective_time',
        ]
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             'effective_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             'date_of_administrative_order': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             'date_of_enrollment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             'graduation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
          }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # إضافة صفات CSS لتحديد الحقول ذات الصلة بالواجهة
        self.fields['institution_name'].widget.attrs.update({'class': 'education-field'})
        self.fields['university_Type'].widget.attrs.update({'class': 'higher-education-field'})
        self.fields['iraqi_university'].widget.attrs.update({'class': 'higher-education-field'})
        self.fields['foreign_university'].widget.attrs.update({'class': 'higher-education-field'})
        self.fields['college'].widget.attrs.update({'class': 'higher-education-field'})
        self.fields['Certificate_Type'].widget.attrs.update({'class': 'higher-education-field'})

    def clean(self):
        cleaned_data = super().clean()
        certificat_minstery_type = cleaned_data.get('certificat_minstery_type')

        # التحقق من الحقول بناءً على نوع الوزارة
        if certificat_minstery_type == 'education':
            if not cleaned_data.get('institution_name'):
                raise forms.ValidationError("اسم المدرسة مطلوب إذا كانت الشهادة صادرة من وزارة التربية.")
        elif certificat_minstery_type == 'higher_education':
            if not any([
                cleaned_data.get('iraqi_university'),
                cleaned_data.get('foreign_university'),
                cleaned_data.get('college'),
            ]):
                raise forms.ValidationError("يرجى تحديد الجامعة أو الكلية إذا كانت الشهادة صادرة من وزارة التعليم العالي.")

        return cleaned_data
    
 


class EmployeeEducationCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="اختر ملف CSV")



class CSVUploadEmployeeEducationForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="الرجاء رفع ملف بصيغة CSV يحتوي على بيانات الشهادات الأكاديمية.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )