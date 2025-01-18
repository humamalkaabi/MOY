from django import forms

from hrhub.models.hr_utilities_models import DutyAssignmentOrder, PlaceOfEmployment


class Duty_Assignment_Order_Form(forms.ModelForm):
    class Meta:
        model = DutyAssignmentOrder
        fields = ['name_in_arabic', 'name_in_english']
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم نوع الامر باللغة العربية'}),
            'name_in_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم نوع الامر باللغة الانكليزية'}),
           
            
        }


from django import forms

class PlaceOfEmploymentForm(forms.ModelForm):
    class Meta:
        model = PlaceOfEmployment
        fields = ['name_in_arabic', 'parent', 'description', 'is_default']
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان المؤسسة باللغة العربية'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'وصف الوظيفة'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PlaceOfEmploymentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات الوزارات أو المؤسسات."
    )