from django import forms

from rddepartment.models.universities_models import ForeignUniversity
from locations.models import Continent, Country


class ForeignUniversityForm(forms.ModelForm):
    class Meta:
        model = ForeignUniversity
        fields = [
            'name_in_english',
            'name_in_arabic',
            'university_name_abbreviation',
            'university_link',
            'country'
        ]
        widgets = {
            'name_in_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الجامعة بالإنجليزية'}),
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الجامعة بالعربية'}),
            'university_name_abbreviation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مختصر اسم الجامعة'}),
            'university_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الجامعة'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
        }


class ForeignUniversityUpdateForm(forms.ModelForm):
    
    class Meta:
        model = ForeignUniversity
        fields = ['country', 'name_in_english', 'name_in_arabic', 'university_name_abbreviation', 'university_link']
        widgets = {
            'name_in_english': forms.TextInput(attrs={'placeholder': 'ادخل اسم الجامعة باللغة الإنجليزية'}),
            'name_in_arabic': forms.TextInput(attrs={'placeholder': 'ادخل اسم الجامعة باللغة العربية'}),
            'university_name_abbreviation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مختصر اسم الجامعة'}),
            'university_link': forms.URLInput(attrs={'placeholder': 'https://www.example.com'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
        }


class ForeignUniversityCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات الجامعات الأجنبية.",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )