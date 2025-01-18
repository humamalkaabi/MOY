

from django import forms
from hrhub.models.employement_models import EmploymentHistory, EmployementType

class EmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = EmploymentHistory
        fields = ['start_date', 'end_date', 'employee_duration_year', 'employee_duration_month', 'employee_duration_day',
                  'employee_type', 'employee_place', 'pdf_file', 'comments']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class EmploymentHistoryCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات خدمات الموظف .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )


