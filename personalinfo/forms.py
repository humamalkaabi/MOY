from django import forms
from .models import BasicInfo, AdditionalInfo, OfficialDocuments, Official_Documents_Type, Nationalism, Religion
from django.forms.widgets import DateInput


class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = [
            'firstname', 'secondname', 'thirdname', 'fourthname', 'surname',
            'mothername', 'phone_number', 'email', 'date_of_birth',
            'place_of_birth', 'gender', 'bio', 'avatar'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.emp_id = kwargs.pop('emp_id', None)
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.emp_id:
            instance.emp_id = self.emp_id
        if self.created_by:
            instance.created_by = self.created_by
        if commit:
            instance.save()
        return instance
    


class ReligionForm(forms.ModelForm):
    class Meta:
        model = Religion
        fields = ['name_in_arabic']  # فقط الحقول التي يجب إدخالها يدوياً
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم الديانة بالعربية'}),
        }




from . models import Nationalism
class NationalismForm(forms.ModelForm):
    class Meta:
        model = Nationalism
        fields = ['name_in_arabic']  # تأكد من تضمين الحقول التي تريدها
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control'}),
        }



class OfficialDocumentsTypeForm(forms.ModelForm):
    class Meta:
        model = Official_Documents_Type
        fields = ['name_in_arabic', 'name_in_english', 'commennts']  # الحقول التي يجب إدخالها
        widgets = {
            'name_in_arabic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم الوثيقة بالعربية'}),
            'name_in_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم الوثيقة بالإنجليزية'}),
            'commennts': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'أدخل ملاحظات عن الوثيقة'}),
        }


class OfficialDocumentForm(forms.ModelForm):
    class Meta:
        model = OfficialDocuments
        fields = [
            'official_documents_type',
            'official_documents_id_number', 
            'issuer', 
            'personal_id_issuance_date',
            'personal_id_expire_date',
            'personal_id_front_page', 
            'personal_id_back_page'
        ]
        widgets = {
            'personal_id_issuance_date': forms.DateInput(attrs={'type': 'date'}),
            'personal_id_expire_date': forms.DateInput(attrs={'type': 'date'}),
        }

# forms.py

class CSVUploadEmployeeOfficialDocumentForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="يرجى تحميل ملف بصيغة CSV يحتوي على البيانات المطلوبة."
    )
class CSVUploadOfficialDocumentForm(forms.Form):
    csv_file = forms.FileField(label="اختر ملف CSV", required=True)



class BasicInfoCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="اختر ملف CSV يحتوي على بيانات الموظفين."
    )

class AdditionalInfoCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="تحميل ملف CSV",
        help_text="اختر ملف CSV يحتوي على بيانات الموظفين."
    )



################## Addition Info

class AdditionalinfoForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = [
            'blood_type',
            'religion',
            'nationalism',
          
            'marital_status',
            'governorate_of_residence',
            'address',
            'emergency_contact_name',
            'emergency_contact_number',
        ]
        widgets = {
          
        }
        help_texts = {
            'blood_type': 'اختر فصيلة الدم الخاصة بالموظف.',
            'religion': 'اختر ديانة الموظف.',
            'nationalism': 'اختر قومية الموظف.',
        }


############################ Update ######################


class UpdateFirstNameForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['firstname']  # تحديد الحقول التي سيتم تعديلها
        help_texts = {
            'firstname': ('يرجى إدخال الاسم الأول الجديد.')
        }

class UpdateSecondNameForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['secondname']  # تحديد الحقل الذي سيتم تعديله (الاسم الثاني)
        help_texts = {
            'secondname': ('يرجى إدخال الاسم الثاني الجديد.')
        }


class UpdateThirdNameForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['thirdname']  # تحديد الحقل الذي سيتم تعديله (الاسم الثالث)
        help_texts = {
            'thirdname': ('يرجى إدخال الاسم الثالث الجديد.')
        }

class UpdateFourthNameForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['fourthname']  # تحديد الحقل الذي سيتم تعديله (الاسم الرابع)
        help_texts = {
            'fourthname': ('يرجى إدخال الاسم الرابع الجديد.')
        }

class UpdateSurnameForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['surname']  # تحديد الحقل الذي سيتم تعديله (اللقب)
        help_texts = {
            'surname': ('يرجى إدخال اللقب الجديد.')
        }


class UpdateMotherNameForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['mothername']  # تحديد الحقل الذي سيتم تعديله (اسم الأم)
        help_texts = {
            'mothername': ('يرجى إدخال اسم الأم الجديد.')
        }

class UpdatePhoneNumberForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['phone_number']  # تحديد الحقل الذي سيتم تعديله (رقم الهاتف)
        help_texts = {
            'phone_number': ('يرجى إدخال رقم الهاتف الجديد.')
        }

class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['email']  # تحديد الحقل الذي سيتم تعديله (البريد الإلكتروني)
        help_texts = {
            'email': ('يرجى إدخال البريد الإلكتروني الجديد.')
        }

class UpdateDateOfBirthForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['date_of_birth']  # حقل تاريخ الميلاد فقط
        help_texts = {
            'date_of_birth': ('يرجى إدخال تاريخ الميلاد الجديد.')
        }
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'})  # تحديد نوع الحقل كـ "تاريخ"
        }

class UpdatePlaceOfBirthForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['place_of_birth']  # فقط حقل مكان الميلاد
        help_texts = {
            'place_of_birth': ('يرجى تحديد محافظة مكان الميلاد الجديد.')
        }

class UpdateGenderForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['gender']  # حقل الجنس فقط
        help_texts = {
            'gender': ('يرجى تحديد جنس الموظف.')
        }

class UpdateBioForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['bio']  # حقل السيرة الذاتية فقط
        help_texts = {
            'bio': ('يرجى إدخال السيرة الذاتية أو تعديلها.')
        }

class UpdateAvatarForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        fields = ['avatar']  # حقل الصورة فقط
        help_texts = {
            'avatar': ('يرجى تحميل صورة جديدة لملفك الشخصي.')
        }


#################################################################


################################### Update Additional Info ###################################

class BloodTypeUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['blood_type'] 
        help_texts = {
            'avatar': ('يرجى اختيار فصيلة الدم .')
        } # عرض فصيلة الدم فقط

class ReligionUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['religion']  # فقط حقل الديانة

class NationalismUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['nationalism']  # فقط حقل القومية


class MaritalStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['marital_status']  # فقط حقل الحالة الاجتماعية

class GovernorateOfResidenceUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['governorate_of_residence']  # فقط حقل مكان الإقامة


class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['address']  # فقط حقل العنوان


class EmergencyContactUpdateForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['emergency_contact_name', 'emergency_contact_number']  # فقط اسم الطوارئ ورقم الطوارئ
