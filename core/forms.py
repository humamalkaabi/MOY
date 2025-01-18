from django import forms
from .models import Main_About_US, Logo

class MainAboutUsForm(forms.ModelForm):
    class Meta:
        model = Main_About_US
        fields = ['title', 'massage', 'phone_number', 'email', 'locations']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # يمكنك تخصيص الحقول هنا مثل تغيير النصوص التوضيحية أو تنسيق الحقول.



class LogoForm(forms.ModelForm):
    class Meta:
        model = Logo
        fields = ['image', 'description']