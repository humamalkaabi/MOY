
from django import forms
from hrhub.models.office_position_models import Office, Position, EmployeeOffice, EmployeeOfficePosition

class OfficeForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الوحدة الإدارية'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class EmployeeCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="يرجى تحميل ملف بصيغة CSV يحتوي على بيانات الموظفين والوحدات الإدارية."
    )
class EmployeeOfficeForm(forms.ModelForm):
    parent_office = forms.ModelChoiceField(
        queryset=Office.objects.filter(parent__isnull=True) | Office.objects.filter(parent__children__isnull=True),
        required=True,
        label="الوحدة الإدارية الرئيسية",
        help_text="اختر الوحدة الإدارية الأعلى."
    )

    office = forms.ModelChoiceField(
        queryset=Office.objects.none(),
        required=True,
        label="الوحدة الإدارية الفرعية",
        help_text="اختر الوحدة الإدارية الفرعية."
    )

    class Meta:
        model = EmployeeOffice
        fields = ['parent_office', 'office', 'start_date', 'end_date', 'comments']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # إذا كان هناك كائن `EmployeeOffice` بالفعل (تحديث)، قم بتحديد القيم المبدئية
        if self.instance.pk:
            self.fields['parent_office'].initial = self.instance.office.parent if self.instance.office else None
            if self.instance.office and self.instance.office.parent:
                self.fields['office'].queryset = Office.objects.filter(parent=self.instance.office.parent)
                self.fields['office'].initial = self.instance.office
        else:
            self.fields['office'].queryset = Office.objects.none()

        # في حال كان المستخدم قد اختار `parent_office` من القائمة
        if 'parent_office' in self.data:
            try:
                parent_office_id = int(self.data.get('parent_office'))
                self.fields['office'].queryset = Office.objects.filter(parent_id=parent_office_id)
            except (ValueError, TypeError):
                pass  # إذا لم يكن هناك تحديد، لا تفعل شيئًا
            
# class EmployeeUpdateOfficeForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeOffice
#         fields = ['office', 'start_date', 'end_date', 'comments']
#         widgets = {
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#             'comments': forms.Textarea(attrs={'rows': 3}),
#         }

class EmployeeOfficeUpdateForm(forms.ModelForm):
    office = forms.ModelChoiceField(
        queryset=Office.objects.all(),
        required=True,
        label="الوحدة الإدارية",
        help_text="اختر الوحدة الإدارية الجديدة للموظف."
    )

    class Meta:
        model = EmployeeOffice
        fields = ['office', 'start_date', 'end_date', 'comments']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'office', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الوظيفة'}),
            'office': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            
        }

class OfficeCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات الوحدات الإدارية."
    )

class EmployeeOfficePositionCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات  المناصب للموظفين."
    )


class PositionCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="ملف CSV",
        help_text="يرجى رفع ملف CSV يحتوي على بيانات  عناوين المناصب ومواقعها ."
    )




class EmployeeOfficePositionForm(forms.ModelForm):
    class Meta:
        model = EmployeeOfficePosition
        fields = ['office', 'position', 'duty_assignment_order', 'is_primary', 'start_date', 
                  'end_date', 'user_employeeofficeposition', 'comments']
        
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }



from django.utils import timezone

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="تاريخ البدء"
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="تاريخ الانتهاء"
    )
    show_all = forms.BooleanField(
        required=False,
        initial=False,
        label=" عرض الكل - بدون فترة محددة"
    )