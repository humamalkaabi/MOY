from django import forms

from rddepartment.models.universities_models import  College




class CollegeForm(forms.ModelForm):
    class Meta:
        model = College
        fields = ['name_in_arabic', 'name_in_english']
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'placeholder': 'ادخل اسم الكلية باللغة العربية'}),
            'name_in_english': forms.TextInput(attrs={'placeholder': 'ادخل اسم الكلية باللغة الانكليزية'}),
           
        }