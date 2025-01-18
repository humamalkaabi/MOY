from django import forms

from rddepartment.models.universities_models import IraqiUniversity

class IraqiUniversityForm(forms.ModelForm):
    class Meta:
        model = IraqiUniversity
        fields = ['name_in_arabic', 'name_in_english', 'university_type', 'governorate', 'address']
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'placeholder': 'ادخل اسم الجامعة باللغة العربية'}),
            'name_in_english': forms.TextInput(attrs={'placeholder': 'ادخل اسم الجامعة باللغة الانكليزية'}),
            'governorate': forms.Select(attrs={'placeholder': 'اختر المحافظة'}),
            'address': forms.Textarea(attrs={'placeholder': 'ادخل عنوان الجامعة'}),
        }



class IraqiUniversityCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات الجامعات العراقية.",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )