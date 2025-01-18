from django import forms
from rddepartment.models.Education_Degree_Type import EducationDegreeType

class EducationDegreeTypeForm(forms.ModelForm):
    class Meta:
        model = EducationDegreeType
        fields = [
            'name_in_arabic', 
            'name_in_english', 
            'grade_number', 
            'step_number', 
            'education_degree_number', 
            'years_effects', 
            'stop_point', 
            'has_effect', 
            'addtion_years_effects', 
            'comments'
        ]
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
