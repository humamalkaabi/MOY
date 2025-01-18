# forms.py
from django import forms
from hrhub.models.grade_step_models import EmployeeGrade, EmployeeStep


class EmployeeGradeForm(forms.ModelForm):
    class Meta:
        model = EmployeeGrade
        fields = ['grade_number', 'name_in_words']  # الحقول المطلوبة
        widgets = {
            'grade_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل رقم الدرجة'}),
            'name_in_words': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم الدرجة كتابة'}),
        }


class EmployeeStepForm(forms.ModelForm):
    class Meta:
        model = EmployeeStep
        fields = ['grade_number', 'name_in_words', 'step_number']  # إضافة step_number
        widgets = {
          
            'name_in_words': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم الدرجة كتابة'}),
            'step_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل رقم المرحلة'}),
        }
    

from hrhub.models.grade_step_upgrade_models import  EmployeeGradeStepSettings, EmployeeGradeStep


class EmployeeGradeStepForm(forms.ModelForm):
    class Meta:
        model = EmployeeGradeStep
        fields = [
            'is_initial_employment', 'start_grade', 'start_step', 'start_grade_date', 'start_step_date',
            'pdf_file', 'auto_start_grade', 'auto_start_date', 'auto_grade_step_upgrade', 
            'future_auto_grade_step_upgrade', 'grade_now', 'step_now', 'grade_temp', 'step_temp',
            'current_grade_start_date', 'total_step_grade_years', 'total_step_grade_months', 'total_step_grade_days',
            'division_rate', 'stop_grade', 'total_years', 'total_months', 'total_days', 'current_deserving',
            'next_deserving', 'future_grade', 'future_step', 'future_effective_date', 'status', 'is_active', 'comments'
        ]
        widgets = {
            'start_grade_date': forms.DateInput(attrs={'type': 'date'}),
            'start_step_date': forms.DateInput(attrs={'type': 'date'}),
            'current_grade_start_date': forms.DateInput(attrs={'type': 'date'}),
            'future_effective_date': forms.DateInput(attrs={'type': 'date'}),
        }

# EmployeeGradeStep
# class EmployeeGradeStepForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeGradeStep
#         exclude = ('basic_info','status', 'total_step_grade_years', 'total_step_grade_months', 'total_step_grade_days', 'grade_temp', 'step_temp', 'created_by', 'slug', 'is_active')  # إزالة حقل الموظف لأنه سيتم تحديده من الـ slug
#         widgets = {
#             'start_grade_date': forms.DateInput(attrs={'type': 'date'}),
#             'start_step_date': forms.DateInput(attrs={'type': 'date'}),
#             'current_grade_start_date': forms.DateInput(attrs={'type': 'date'}),
#             'current_step_start_date': forms.DateInput(attrs={'type': 'date'}),
#             'future_effective_date': forms.DateInput(attrs={'type': 'date'}),
#         }

# class EmployeeGradeStepStatusForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeGradeStep
#         fields = ['status']  # فقط حقل الحالة
#         widgets = {
#             'status': forms.Select(choices=EmployeeGradeStep.STATUS_CHOICES),
#         }


# class EmployeeGradeStepCSVUploadForm(forms.Form):
#     csv_file = forms.FileField(
#         label="ملف CSV",
#         help_text="يرجى تحميل ملف بصيغة CSV يحتوي على البيانات المراد إدخالها.",
#     )




class EmployeeGradeCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات الدرجات الوظيفية."
    )

class EmployeeStepCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات المراحل الوظيفية."
    )


class EmployeeGradeStepSettingsForm(forms.ModelForm):
    class Meta:
        model = EmployeeGradeStepSettings
        fields = ['auto_grade_step_upgrade', 'future_auto_grade_step_upgrade']
        labels = {
            'auto_grade_step_upgrade': "حساب العلاوة والترفيع تلقائياً",
            'future_auto_grade_step_upgrade': "حساب العلاوة والترفيع القادم تلقائياً",
        }
        widgets = {
            'auto_grade_step_upgrade': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'future_auto_grade_step_upgrade': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# class EmployeeGradeStepForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeGradeStep
#         fields = '__all__'  # يمكنك تحديد الحقول التي تريدها بدلاً من ذلك
#         exclude = ['employee', 'created_by', 'slug', 'total_years', 'total_months', 'total_days', 'total_step_grade_days', 'total_step_grade_months', 'total_step_grade_years', 'step_temp', 'grade_temp']

#         widgets = {
#             'start_grade_date': forms.DateInput(attrs={'type': 'date'}),
#             'start_step_date': forms.DateInput(attrs={'type': 'date'}),
#             'current_grade_start_date': forms.DateInput(attrs={'type': 'date'}),
#             'future_effective_date': forms.DateInput(attrs={'type': 'date'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super(EmployeeGradeStepForm, self).__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'  # تحسين التصميم مع Bootstrap