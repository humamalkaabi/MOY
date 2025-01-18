# forms.py
from django import forms
from .models import Governorate, Region, Continent, Country

class GovernorateForm(forms.ModelForm):
    class Meta:
        model = Governorate
        fields = ['name_english', 'name_arabic', 'description']

class GovernorateCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV فقط.",
    )

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['governorate', 'name_english', 'name_arabic', 'description']

class RegionCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على البيانات المطلوبة للمناطق."
    )

class ContinentForm(forms.ModelForm):
    class Meta:
        model = Continent
        fields = ['name_english', 'name_arabic']


class CountryCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على البيانات المطلوبة."
    )

      

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['continent', 'name_english', 'name_arabic']
