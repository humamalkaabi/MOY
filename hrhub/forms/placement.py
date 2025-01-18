from django import forms
from hrhub.models.placement_models import Placement

class PlacementForm(forms.ModelForm):
    class Meta:
        model = Placement
        fields = [
           
            'placement_type', 
            'place_of_placement', 
            'name', 
            'pdf_file', 
            'start_date', 
            'end_date'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }





class PlacementCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات الملاك للموظفين .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )