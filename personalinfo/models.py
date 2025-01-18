from django.db import models
# استيرادات مكتبات Django
from django.db import models  # استيراد الوحدة models من Django لإنشاء النماذج (Models) التي تمثل قواعد البيانات
from django.utils.text import slugify  # استيراد الدالة slugify لتحويل النصوص إلى صيغ URL قابلة للاستخدام
from django.utils.translation import gettext_lazy as _  # استيراد الدالة gettext_lazy لترجمة النصوص (تأجيل الترجمة حتى الحاجة إليها)
from django.core.validators import RegexValidator, EmailValidator  # استيراد المدققين (Validators) للتحقق من صحة المدخلات مثل النصوص والبريد الإلكتروني
from django.core.exceptions import ValidationError  # استيراد الاستثناء ValidationError للتعامل مع الأخطاء المتعلقة بالتحقق من المدخلات
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن
from django.dispatch import receiver  # استيراد المستلم (Receiver) لربط الإشارات مع الدوال التي يجب تنفيذها عند حدوث الإشارة
# استيرادات مكتبات خارجية
import io  # استيراد مكتبة io للعمل مع البيانات الثنائية، مثل الملفات والصور
from unidecode import unidecode  # استيراد دالة unidecode لتحويل النصوص غير اللاتينية (مثل العربية) إلى نصوص لاتينية مشابهة
from PIL import Image  # استيراد مكتبة PIL (Pillow) للتعامل مع الصور في Python

# استيرادات النماذج من تطبيقات داخل المشروع
from accounts.models import Employee  # استيراد النموذج Employee من تطبيق accounts (تطبيق يحتوي على معلومات الموظفين)
from locations.models import Governorate
# Create your models here.  # هذا تعليق عام يطلب منك إنشاء النماذج في هذا الملف
from datetime import date



GENDER_MALE = 'M'  # رمز ذكر
GENDER_FEMALE = 'F'  # رمز أنثى


GENDER_CHOICES = [
    (GENDER_MALE, _('ذكر')),
    (GENDER_FEMALE, _('أنثى')),
]

def user_avatar_path(instance, filename):
    """Generate avatar upload path based on employee ID."""
    return f'image/users/avatar/{instance.emp_id.username}/avatar/{filename}'



class BasicInfo(models.Model):
    emp_id = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='basic_info',
        help_text=_("الموظف المرتبط بهذه المعلومات الأساسية.")
    )

    firstname = models.CharField(max_length=50,
                                 verbose_name="الاسم الاول ",
                                   help_text=_("الاسم الأول للموظف."))
    secondname = models.CharField(max_length=50,
                                   verbose_name="الاسم الثاني ",
                                   help_text=_("الاسم الثاني للموظف."))
    thirdname = models.CharField(max_length=50,
                                  verbose_name="الاسم الثالث ",
                                    help_text=_("الاسم الثالث للموظف."))
    fourthname = models.CharField(max_length=50, 
                                null=True, 
                                blank=True, 
                                 verbose_name="الاسم الرابع ",
                                help_text=_("الاسم الرابع للموظف."))
    surname = models.CharField(max_length=50, 
                                null=True, 
                                blank=True, 
                                 verbose_name="اللقب  ",
                                help_text=_("لقب الموظف."))
    
    mothername = models.CharField(max_length=50, 
                                null=True, 
                                blank=True, 
                                 verbose_name="اسم الوالدة  ",
                                help_text=_("اسم والدة الموظف."))
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        null=True, 
        blank=True, 
        validators=[RegexValidator(regex=r'^\d{11}$', message=_('يجب أن يكون رقم الهاتف 11 رقماً فقط.'))],
         verbose_name="رقم الهاتف  ",
        help_text=_('مطلوب. 11 رقماً فقط.')
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null= True,
        max_length=255,
        validators=[EmailValidator(message=_("أدخل عنوان بريد إلكتروني صحيح."))],
         verbose_name="البريد الالكتروني  ",
        help_text=_("عنوان البريد الإلكتروني الفريد للموظف.")
    )
    date_of_birth = models.DateField(null=True, blank=True, 
                                      verbose_name="تاريخ الميلاد  ",
                                      help_text=_("تاريخ ميلاد الموظف (اختياري)."))
    
    place_of_birth = models.ForeignKey(
                Governorate,  # الربط بنموذج Governorate
                on_delete=models.SET_NULL,  # إذا تم حذف المحافظة، يبقى الحقل فارغًا
                null=True, blank=True,  # الحقل اختياري
                related_name='basicinfo_place_of_birth', 
                  verbose_name=" محل الميلاد ",
                help_text=_("المحافظة التي وُلد فيها الموظف.")  # النص التوضيحي للمستخدم
                )

    gender = models.CharField(max_length=1,
                              null=True, 
                                blank=True, 
                                 verbose_name="جنس الموظف  ",
                                  choices=GENDER_CHOICES, help_text=_("جنس الموظف."))
    bio = models.TextField(null=True, 
        blank=True,  help_text=_("سيرة قصيرة للموظف (اختياري)."))
    
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True, 
        blank=True, 
         verbose_name="صورة شخصية  ",
        help_text=_("صورة ملف تعريف الموظف (اختياري).")
    )

    slug = models.SlugField(max_length=100,unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))
    
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_basic_infos',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الأساسية.")
    )

    is_approved = models.BooleanField(
        default=True,
        verbose_name=_("معلومات أساسية معتمدة"),
        help_text=_("تشير إلى ما إذا كانت المعلومات الأساسية معتمدة.")
    )
    emplpyee_age = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("عمر الموظف  ")
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('معلومات أساسية')
        verbose_name_plural = _('معلومات أساسية')
        indexes = [
            models.Index(fields=['emp_id']),
            models.Index(fields=['phone_number']),
        ]
        permissions = [
    ("can_access_employee_dashboard", "يمكنه الوصول الى لوحة تحكم الموظفين   "),
    ("can_add_employee_basic_info", "يمكنه اضافة بيانات  اساسية للموظف       "),
     ("can_view_employee_basic_info", "يمكنه عرض بيانات  اساسية للموظف       "),
    ("can_update_employee_basic_info", "يمكنه تحديث البيانات  الاساسية للموظف       "),
    ("can_delete_employee_basic_info", "يمكنه حذف البيانات  الاساسية للموظف       "),
    ("can_update_firstname", "يمكن تحديث الاسم الأول"),
    ("can_update_secondname", "يمكن تحديث الاسم الثاني"),
    ("can_update_thirdname", "يمكن تحديث الاسم الثالث"),
    ("can_update_fourthname", "يمكن تحديث الاسم الرابع"),
    ("can_update_surname", "يمكن تحديث اللقب"),
    ("can_update_mothername", "يمكن تحديث اسم الأم"),
    ("can_update_phonenumber", "يمكن تحديث رقم الهاتف"),
    ("can_update_email", "يمكن تحديث البريد الإلكتروني"),
    ("can_update_date_of_birth", "يمكن تحديث تاريخ الميلاد"),
    ("can_update_place_of_birth", "يمكن تحديث مكان الميلاد"),
    ("can_update_gender", "يمكن تحديث الجنس"),
    ("can_update_bio", "يمكن تحديث السيرة الذاتية"),
    ("can_update_avatar", "يمكن تحديث الصورة الشخصية"),
    ("can_quick_search", "لديه  القدرة على الوصول الى ايقونه البحث السريع   "),
     ("can_access_control_panel", "لديه  القدرة على الوصول الى لوحة التحكم الادارية      "),
]

    def get_description(self):
        return _(" هذا الجدول يهتم  المعلومات الاساسية للموظف من الاسم الاول والاسم الثاني والثالث والرابع واللقب و اسم الام ورقم الهاتف و الايميل وجنس الموظف و تاريخ الميلاد ومحل الولادة و صورة  الموظف و السيرة الذاتية و تفعيل دخول الموظف  الى صفحته الشخصية     .")


    def save(self, *args, **kwargs):
        if not self.firstname or not self.secondname or not self.thirdname:
            raise ValidationError(_('يجب إدخال جميع الأسماء الأساسية للموظف'))
        

        
        

        if self.date_of_birth:
            today = date.today()
            self.emplpyee_age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        
        # إنشاء سلاج فريد إذا لم يكن موجوداً
        if not self.slug:
            base_slug = slugify(unidecode(f"{self.firstname} {self.secondname} {self.thirdname}".strip()))
            unique_slug = base_slug
            count = 1
            while BasicInfo.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{count}"
                count += 1
            self.slug = unique_slug
        
        super().save(*args, **kwargs)
    
   
    
    
    def get_full_name(self):
        return " ".join(filter(None, [self.firstname, self.secondname, self.thirdname])).strip()

    def __str__(self):
        return self.get_full_name()
    
    
class Official_Documents_Type(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='official_documents_type_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )
    name_in_arabic = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم الوثيقة  بالعربية"),
        help_text=_("يرجى إدخال اسم الوثيقة بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("اسم الوثيقة  بالانكليزية"),
        help_text=_("يرجى إدخال اسم الوثيقة بالانكليزية.")
    )
    commennts = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن  الوثيقة  "),
        help_text=_("ملاحظات عن الوثيقة   ")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم الشهادة (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('نوع الوثيقة الرسمية  ')
        verbose_name_plural = _('انواع  الوثائق الرسمية ')
        permissions = [
           
            ("can_create_official_documents_type", _("اضافة نوع وثيقة رسمية ")),
            ("can_update_official_documents_type", _("تحديث الوثيقة الرسمية")),
            ("can_delete_official_documents_type", _("حذف الوثيقة الرسمية")),
        ]
    def get_description(self):
        return "يتعامل هذا الجدول مع نوع الوثيقة الرسمية  من حيث إضافة  جديدة أو تحديث اسم  موجود أو حذفه."

    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while Official_Documents_Type.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(Official_Documents_Type, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية
    
    def __str__(self):
        return self.name_in_arabic
    

def user_personal_id_path(instance, filename):
    if not hasattr(instance.basic_info, 'emp_id') or not hasattr(instance.basic_info.emp_id, 'username'):
        raise ValueError("المعلومات الأساسية أو الرقم الوظيفي غير متوفر")
    
    employee_number = instance.basic_info.emp_id.username
    return f'image/users/{employee_number}/personal_id/{filename}'


class OfficialDocuments(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='official_documents_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )

    official_documents_type = models.ForeignKey(
        Official_Documents_Type, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='official_documents_type',
        verbose_name="نوع الوثيقة",
        help_text=_("    يرجى اختيار نوع الوثيقة الرسمية  مثل بطاقة وطنية او غيرها    .")
    )

    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employee_official_documents',
        verbose_name=_("رقم الموظف"),
        help_text=_("اختر الموظف المرتبط بهذه الوئيقة.")
    )
    official_documents_id_number = models.CharField(
    max_length=30,  
    unique=True,
    null=True,
    blank=True,
    verbose_name=" رقم الوثيقة",
    help_text=_("رقم الوثيقة  الرسمية.")
)
    issuer = models.ForeignKey(
                Governorate,  # الربط بنموذج Governorate
                on_delete=models.SET_NULL,  # إذا تم حذف المحافظة، يبقى الحقل فارغًا
                null=True, blank=True,  # الحقل اختياري
                related_name='official_documents_id_issuer',
                verbose_name=" جهة اصدار الوثيقة ",  # الاسم المرجعي للعلاقة العكسية
                help_text=_("المحافظة التي تم اصدار الوثيقة منها-اختياري .")  # النص التوضيحي للمستخدم
                )
    
    personal_id_issuance_date = models.DateField(null=True, blank=True, 
                                                 verbose_name=" تاريخ صدور الوثيقة   ", 
                                                 help_text=_("تاريخ صدور الوثيقة  (اختياري)."))
    
    personal_id_expire_date = models.DateField(null=True, blank=True,
                                               verbose_name=" تاريخ انتهاء  الوثيقة ", 
                                                help_text=_("تاريخ انتهاء الوثيقة  (اختياري)."))

    personal_id_front_page = models.ImageField(
        upload_to=user_personal_id_path,
        null=True,
        blank=True, 
       verbose_name=" الصفحة الامامية للوثيقة   ", 
        help_text=_("الواجهة الامامية للبطاقة الوطنية للموظف")
        )      

    personal_id_back_page = models.ImageField(
        upload_to=user_personal_id_path,
        null=True,
        blank=True, 
        verbose_name=" الصفحة الخلفية للوثيقة   ", 

       
        help_text=_("الواجهة الخلفية للبطاقة الوطنية للموظف")
        )      
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم الشهادة (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))
    class Meta:
        ordering = ['created_at']
        verbose_name = _(' الوثيقة الرسمية ')
        verbose_name_plural = _('  الوثائق الرسمية ')
        constraints = [
            models.UniqueConstraint(
                fields=['basic_info', 'official_documents_type'],
                name='unique_employee_document_type'
            )
        ]
        
        permissions = [
             ("can_view_official_documents", _("عرض  وثيقة رسمية للموظف ")),
            ("can_create_official_documents", _("اضافة  وثيقة رسمية للموظف ")),
            ("can_update_official_documents", _("تحديث الوثيقة الرسمية للموظف")),
            ("can_delete_official_documents", _("حذف الوثيقة الرسمية للموظف")),
        ]
    
    def get_description(self):
        return "يتعامل هذا الجدول مع الوثيقة الرسمية للموظفين  من حيث إضافة  جديدة أو تحديث اسم  موجود أو حذفه."
    
    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.basic_info:
            self.slug = slugify(unidecode(self.basic_info.thirdname))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while OfficialDocuments.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(OfficialDocuments, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية



class Religion(models.Model):
    created_by = models.ForeignKey(
        Employee,  # استبدل 'Employee' بالنموذج الصحيح إذا كان في تطبيق مختلف
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='religion_employment_info',
        verbose_name=_("موظف الديانة"),
        help_text=_("الموظف الذي قام بإنشاء هذه المعلومات الخاصة بالديانة.")
    )
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم الديانة بالعربية"),
        help_text=_("يرجى إدخال اسم الديانة بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("اسم  الديانة بالانكليزية"),
        help_text=_("يرجى إدخال اسم الديانة بالانكليزية.")
    )
    commennts = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن  الديانة  "),
        help_text=_("ملاحظات عن الديانة   ")
    )
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('معلومات الديانات')
        verbose_name_plural = _('معلومات الديانة')
        permissions = [
           
            ("can_create_religion", _("اضافة ديانة")),
            ("can_update_religion", _("تحديث الديانة")),
            ("can_delete_religion", _("حذف الديانة")),
        ]


        

    def get_description(self):
        return "يتعامل هذا الجدول مع الديانة من حيث إضافة اسم ديانة جديدة أو تحديث اسم ديانة موجودة أو حذفها."

    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while Religion.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(Religion, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية

    def __str__(self):
        return self.name_in_arabic

class Nationalism(models.Model):
    created_by = models.ForeignKey(
        Employee,  # استبدل 'Employee' بالنموذج الصحيح إذا كان في تطبيق مختلف
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nationalism_employment_info',
        verbose_name=_("موظف القومية"),
        help_text=_("الموظف الذي قام بإنشاء هذه المعلومات الخاصة بالقومية.")
    )
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم القومية بالعربية"),
        help_text=_("يرجى إدخال اسم القومية بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("اسم القومية  بالانكليزية"),
        help_text=_("يرجى إدخال اسم القومية بالانكليزية.")
    )
    commennts = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن  الوثيقة  "),
        help_text=_("ملاحظات عن الوثيقة   ")
    )
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للقومية (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('معلومات القوميات')
        verbose_name_plural = _('معلومات القومية')
        permissions = [
           
            ("can_create_nationalism", _("اضافة قومية")),
            ("can_update_nationalism", _("تحديث القومية")),
            ("can_delete_nationalism", _("حذف القومية")),
        ]


    def get_description(self):
        return "يتعامل هذا الجدول مع القومية من حيث إضافة اسم قومية جديدة أو تحديث اسم قومية موجودة أو حذفها."

    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while Nationalism.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(Nationalism, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية

    def __str__(self):
        return self.name_in_arabic
    


class AdditionalInfo(models.Model):
    """
    A model to store additional personal information for an employee.
    """
    basic_info = models.OneToOneField(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='additional_info'
    )

    blood_type = models.CharField(
        max_length=3,
        choices=[
            ('A', _('A')),
            ('B', _('B')),
            ('AB', _('AB')),
            ('O', _('O')),
            ('A-', _('A-')),
            ('B-', _('B-')),
            ('AB-', _('AB-')),
            ('O-', _('O-')),
        ],
        blank=True,  # يمكن أن يكون الحقل فارغًا
        null=True,
        help_text=_("فصيلة دم الموظف.")
    )

    religion = models.ForeignKey(
        Religion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employeereligion',
        verbose_name=_("religion"),
        help_text=_("اختر ديانة الموظف.")
    )

    nationalism = models.ForeignKey(
        Nationalism,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employeenationalism',
        verbose_name=_("nationalism"),
        help_text=_("اختر قومية الموظف.")
    )
   

    marital_status = models.CharField(
        max_length=20,
        choices=[
            ('single', _('أعزب')),
            ('married', _('متزوج')),
            ('divorced', _('مطلق')),
            ('widowed', _('أرمل'))
        ],
        null=True,
        blank=True,
        help_text=_("الحالة الاجتماعية للموظف.")
    )
    governorate_of_residence = models.ForeignKey(
        Governorate,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='additional_infos',
        help_text=_("المحافظة التي يسكن فيها الموظف    ")
    )
    address = models.TextField(null=True,
        blank=True,help_text=_("عنوان الموظف."))

    emergency_contact_name = models.CharField(max_length=100,
                                            null=True,
                                            blank=True,  help_text=_("اسم الشخص للطوارئ."))
    emergency_contact_number = models.CharField(
        max_length=15,
        null=True,
        blank=True, 
        validators=[RegexValidator(regex=r'^\d{11}$', message=_('يجب أن يكون رقم الطوارئ 11 رقمًا.'))],
        help_text=_("رقم هاتف الطوارئ.")
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف."))
    
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='additional_infos_created_by',
        help_text=_("المستخدم الذي قام بإنشاء أو تحديث هذه المعلومات.")
    )
    is_approved = models.BooleanField(
        default=False, 
        verbose_name=_("معلومات إضافية معتمدة"), 
        help_text=_("تشير إلى ما إذا كانت المعلومات الإضافية معتمدة.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['created_at']
        verbose_name = _('معلومات اضافية')
        verbose_name_plural = _('معلومات اضافية')
        permissions = [
            ("can_add_employee_additional_info", "يمكنه اضافة بيانات  اضافية للموظف       "),
            ("can_view_employee_additional_info", "يمكنه عرض البيانات  الاضافية للموظف       "),
            ("can_update_employee_additional_info", "يمكنه تحديث البيانات  الاضافية للموظف       "),
            ("can_delete_employee_additional_info", "يمكنه حذف البيانات  الاضافية للموظف       "),

            ("can_update_blood_type", _("يمكن تحديث فصيلة الدم")),
            ("can_update_religion", _("يمكن تحديث الديانة")),
            ("can_update_nationalism", _("يمكن تحديث القومية")),
            ("can_update_marital_status", _("يمكن تحديث الحالة الاجتماعية")),
            ("can_update_governorate_of_residence", _("يمكن تحديث مكان الإقامة")),
            ("can_update_address", _("يمكن تحديث العنوان")),
            ("can_update_emergency_contact", _("يمكن تحديث بيانات الطوارئ")),
]
    def get_description(self):
        return ("يتعامل هذا الجدول مع المعلومات الاضافية للموظف مثل فصيلة الدم والحالة الاجتماعية والديانة والقومية ومحافظة السكن وعنوان السكن والاتصال بالرقم البديل او الطوارئ        ")


    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.basic_info:
            self.slug = slugify(unidecode(f"{self.basic_info.firstname}-{self.basic_info.secondname}"))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while AdditionalInfo.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(AdditionalInfo, self).save(*args, **kwargs)

    def __str__(self):
        return f"معلومات إضافية {self.basic_info.get_full_name()}"



######################################## Log #################################
# نموذج سجل تغييرات معلومات أساسية
class BasicInfoChangeLog(models.Model):
    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات أساسية")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغييرات المعلومات الأساسية")
        verbose_name_plural = _("سجلات تغييرات المعلومات الأساسية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.basic_info} - {self.action} - {self.timestamp}"

                #### OfficialDocumentsTypeChangeLog #### 
# نموذج سجل تغييرات أنواع الوثائق الرسمية
class OfficialDocumentsTypeChangeLog(models.Model):
    official_document_type = models.ForeignKey(
        Official_Documents_Type,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع الوثيقة الرسمية")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغييرات نوع الوثيقة الرسمية")
        verbose_name_plural = _("سجلات تغييرات أنواع الوثائق الرسمية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.official_document_type} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات الوثائق الرسمية
class OfficialDocumentsChangeLog(models.Model):
    official_document = models.ForeignKey(
        OfficialDocuments,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الوثيقة الرسمية")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغييرات الوثيقة الرسمية")
        verbose_name_plural = _("سجلات تغييرات الوثائق الرسمية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.official_document} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات الديانة
class ReligionChangeLog(models.Model):
    religion = models.ForeignKey(
        Religion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات الديانة")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغييرات الديانة")
        verbose_name_plural = _("سجلات تغييرات الديانة")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.religion} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات القومية
class NationalismChangeLog(models.Model):
    nationalism = models.ForeignKey(
        Nationalism,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات القومية")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغييرات القومية")
        verbose_name_plural = _("سجلات تغييرات القومية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.nationalism} - {self.action} - {self.timestamp}"



# نموذج سجل تغييرات المعلومات الإضافية
class AdditionalInfoChangeLog(models.Model):
    additional_info = models.ForeignKey(
        AdditionalInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات إضافية")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغييرات المعلومات الإضافية")
        verbose_name_plural = _("سجلات تغييرات المعلومات الإضافية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.additional_info} - {self.action} - {self.timestamp}"


######################################## Signals  ########################
                ####### BasicInfo ###########
@receiver(pre_save, sender=BasicInfo)
def log_basic_info_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = BasicInfo.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            BasicInfoChangeLog.objects.create(
                basic_info=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=BasicInfo)
def log_basic_info_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        BasicInfoChangeLog.objects.create(
            basic_info=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=BasicInfo)
def log_basic_info_deletion(sender, instance, **kwargs):
    BasicInfoChangeLog.objects.create(
        basic_info=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


                #### Signals ####
# الإشارات (Signals) الخاصة بـ Official_Documents_Type
@receiver(pre_save, sender=Official_Documents_Type)
def log_official_document_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Official_Documents_Type.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            OfficialDocumentsTypeChangeLog.objects.create(
                official_document_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Official_Documents_Type)
def log_official_document_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        OfficialDocumentsTypeChangeLog.objects.create(
            official_document_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Official_Documents_Type)
def log_official_document_type_deletion(sender, instance, **kwargs):
    OfficialDocumentsTypeChangeLog.objects.create(
        official_document_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


                #### Signals OfficialDocuments ####
# الإشارات (Signals) الخاصة بـ OfficialDocuments
@receiver(pre_save, sender=OfficialDocuments)
def log_official_document_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = OfficialDocuments.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            OfficialDocumentsChangeLog.objects.create(
                official_document=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=OfficialDocuments)
def log_official_document_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        OfficialDocumentsChangeLog.objects.create(
            official_document=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=OfficialDocuments)
def log_official_document_deletion(sender, instance, **kwargs):
    OfficialDocumentsChangeLog.objects.create(
        official_document=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


            #### Signals Religion ####
# الإشارات (Signals) الخاصة بـ Religion
@receiver(pre_save, sender=Religion)
def log_religion_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Religion.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            ReligionChangeLog.objects.create(
                religion=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Religion)
def log_religion_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        ReligionChangeLog.objects.create(
            religion=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Religion)
def log_religion_deletion(sender, instance, **kwargs):
    ReligionChangeLog.objects.create(
        religion=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


            #### Signals Nationalism ####
# الإشارات (Signals) الخاصة بـ Nationalism
@receiver(pre_save, sender=Nationalism)
def log_nationalism_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Nationalism.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            NationalismChangeLog.objects.create(
                nationalism=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Nationalism)
def log_nationalism_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        NationalismChangeLog.objects.create(
            nationalism=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Nationalism)
def log_nationalism_deletion(sender, instance, **kwargs):
    NationalismChangeLog.objects.create(
        nationalism=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )

# الإشارات (Signals) الخاصة بـ AdditionalInfo
@receiver(pre_save, sender=AdditionalInfo)
def log_additional_info_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = AdditionalInfo.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            AdditionalInfoChangeLog.objects.create(
                additional_info=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=AdditionalInfo)
def log_additional_info_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        AdditionalInfoChangeLog.objects.create(
            additional_info=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=AdditionalInfo)
def log_additional_info_deletion(sender, instance, **kwargs):
    AdditionalInfoChangeLog.objects.create(
        additional_info=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )