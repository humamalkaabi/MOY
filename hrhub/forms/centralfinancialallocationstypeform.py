from django import forms
from hrhub.models.central_financial_allocations_models import CentralFinancialAllocationsType, CentralFinancialAllocations


class CentralFinancialAllocationsTypeForm(forms.ModelForm):
    class Meta:
        model = CentralFinancialAllocationsType
        fields = ['name_in_arabic', 'name_in_english', 'ratio', 'word_ratio', 'comments']
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المخصصات بالعربية'}),
            'name_in_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المخصصات بالإنجليزية'}),
            'ratio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل نسبة المخصصات'}),
            'word_ratio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل نسبة المخصصات كتابة'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'أدخل الملاحظات'}),
        }





class CentralFinancialAllocationsForm(forms.ModelForm):
    class Meta:
        model = CentralFinancialAllocations
        fields = [
           'centralfinancialallocationstype',
           
            'order_number',
            'order_time',
            'effective_time',
            'serial_namber',
            'mac_namber',
            'residency',
            'vechile_name',
            'vechile_number',
            'vechile_line',
            'healthy_cen',
            'name_prevois',
            'comments'
        ]
        widgets = {
            'order_time': forms.DateInput(attrs={'type': 'date'}),
            'effective_time': forms.DateInput(attrs={'type': 'date'}),
        }







class FinancialAllocationsCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="رفع ملف CSV",
        help_text="يرجى رفع ملف بصيغة CSV يحتوي على بيانات خدمات الموظف .",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )


