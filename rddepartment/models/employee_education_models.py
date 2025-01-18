from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from unidecode import unidecode
from accounts.models import Employee
# Content types
from hrhub.models.grade_step_models import EmployeeGrade, EmployeeStep
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن
from locations.models import Country, Governorate
from rddepartment.models.universities_models import College, IraqiUniversity, ForeignUniversity
from rddepartment.models.Education_Degree_Type import EducationDegreeType
from personalinfo.models import BasicInfo
from hrhub.models.hr_utilities_models import DutyAssignmentOrder


class EmployeeEducation(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='school_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الخاصة بالمدرسة.")
    )

    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employee_education',
        verbose_name=_("رقم الموظف"),
        help_text=_("اختر الموظف المرتبط بهذه الشهادة.")
    )
    
    education_degree_type = models.ForeignKey(
        EducationDegreeType,
        on_delete=models.CASCADE,
        null=True, 
        blank=True, 
        related_name='employee_education_type',
        verbose_name=_("نوع الشهادة"),
        help_text=_("اختر نوع الشهادة.")
    )
    
    Certificate_Choices = [
        ('education', _('وزارة التربية')),
        ('higher_education', _('وزارة التعليم العالي ')),
    ]
    Certificate_Type_Choices  = [
        ('original', _('شهادة التعيين ')),
        ('adition_cer', _('شهادة مضافة ')),
    ]
    university_Type_Choices  = [
        ('iraqi_university', _('جامعة عراقية  ')),
        ('foreign_university', _('شهادة اجنبية ')),
    ]


    Certificate_Type = models.CharField(
        max_length=50,
        default='original',
        null=True, 
        blank=True, 
        choices=Certificate_Type_Choices ,
        verbose_name=_("نوع الشهادة - تعين او مضافة "),
        help_text=_("اختر الشهادة   .")
    )

    certificat_minstery_type = models.CharField(
        max_length=50,
        null=True, 
        blank=True, 
        choices=Certificate_Choices,
        verbose_name=_("الوزارة المانحة"),
        help_text=_("اختر الوزارة المانحة للشهادة.")
    )


    institution_name = models.CharField(
        max_length=255,
        null=True, 
        blank=True, 
        verbose_name=_("اسم المدرسة "),
        help_text=_("الرجاء إدخال اسم المدرسة  .")
    )

    university_Type = models.CharField(
        max_length=50,
        default='iraqi_university',
        choices=university_Type_Choices ,
         null=True, 
        blank=True, 
        verbose_name=_("نوع الجامعة "),
        help_text=_("يرجى اختيار نوع الجامعة اذا كاننت عراقية ام اجنبية اختياري    .")
    )
    # الحقول التي تظهر فقط إذا تم اختيار "تعليم عالي"
    iraqi_university = models.ForeignKey(
        IraqiUniversity,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employee_iraqi_university',
        verbose_name=_(" الجامعة العراقية"),
        help_text=_(" يرجى ادخال اسم الجامعة العراقية .")
    )
    foreign_university = models.ForeignKey(
        ForeignUniversity,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employee_foreign_university',
        verbose_name=_(" الجامعة الاجنبية"),
        help_text=_(" يرجى ادخال اسم الجامعة الاجنبية .")
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        null=True, 
        blank=True, 
        related_name='employee_college',
        verbose_name=_("الكلية"),
        help_text=_("الكلية.")
    )
    Certificate_Type = models.CharField(
        max_length=50,
         null=True, 
        blank=True, 
      
        verbose_name=_("التخصص الدقيق "),
        help_text=_("يرجى ادخال التخصص الدقيق في حال الجامعات اختياري    .")
    )

    date_issued = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("تاريخ اصدار الشهادة"),
        help_text=_("أدخل تاريخ إصدار الشهادة.")
    )

    
    duty_assignment_order = models.ForeignKey(
        DutyAssignmentOrder,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='certificate_duty_assignment_order',
        verbose_name=_("نوع الامر"),
        help_text=_("الرجاء اختيار نوع الامر الصادر بالشهادة.")
    )

    duty_assignment_number = models.CharField(
        max_length=255,
        null=True, 
        blank=True, 
        verbose_name=_("رقم الامر "),
        help_text=_("الرجاء إدخال  رقم الامر  .")
    )

    date_of_administrative_order = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ  الامر"),
        help_text=_("أدخل تاريخ  الامر  الخاص بالشهادة.")
    )
    date_of_enrollment = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ المباشرة بالدراسة "),
        help_text=_("أدخل تاريخ المباشرة بالدراسة .")
    )
    graduation_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ التخرج  "),
        help_text=_("أدخل تاريخ التخرج  .")
    )
    certificate_file = models.FileField(
        upload_to='certificates/pdfs/',
        verbose_name=_("ملف الشهادة"),
        help_text=_("قم بتحميل ملف PDF الخاص بالشهادة الأكاديمية."),
        null=True,
        blank=True
    )
    effective_time = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("تاريخ تنفيذ الامر"),
        help_text=_("أدخل تاريخ  احتساب الشهادة للامور الادارية.")
    )
    first_approved = models.BooleanField(
        null=True, 
        blank=True, 
        verbose_name=_("توثيق قسم الدراسات  "),
        help_text=_("تشير إلى ما اذا كان القسم المسؤول عن الدراسات قد وثق الشهادة     .")
    )
    second_approved = models.BooleanField(
        null=True, 
        blank=True, 
        verbose_name=_("توثيق  الادارية  "),
        help_text=_("تشير إلى ما اذا كان القسم المسؤول عن الامور الادارية قد وثق الشهادة     .")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("معرف فريد"),
        help_text=_("معرف فريد مكون من رقم الموظف، نوع الدرجة، الكلية وتاريخ الإصدار.")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التعديل")
    class Meta:
        verbose_name = _("شهادة أكاديمية")
        verbose_name_plural = _("الشهادات الأكاديمية")
        ordering = ['institution_name']
        permissions = [
                ("can_add_employee_education", "يمكن إضافة  شهادة اكاديمية للموظف"),
                ("can_update_employee_education", "يمكن تحديث  شهادة اكاديمية للموظيف"),
                ("can_delete_employee_education", "يمكن حذف  شهادة اكاديمية للموظف"),
        ]

    def save(self, *args, **kwargs):
        # إذا لم يكن هناك قيمة لـ `slug`، قم بإنشائه
        if not self.slug:
    # إنشاء الـ slug الأساسي
            base_slug = slugify(unidecode(f"{self.basic_info.emp_id}-{self.Certificate_Type}-{self.date_issued}"))
            self.slug = base_slug

    # الاحتفاظ بـ slug الأصلي للتحقق في حالة وجود تكرار
            original_slug = self.slug
            counter = 1

    # التحقق من وجود slug مكرر
            while EmployeeEducation.objects.filter(slug=self.slug).exists():  # قم بتغيير `Certificate` إلى اسم النموذج الخاص بك
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    @classmethod
    def get_latest_certificate(cls, employee):
    # استعلام لتحميل أحدث شهادة بناءً على تاريخ التنفيذ
        latest_certificate = cls.objects.filter(basic_info=employee) \
        .select_related('education_degree_type') \
        .order_by('-effective_time') \
        .first()

    # إذا كانت الشهادة موجودة وتم العثور على نوع الشهادة، إرجاع الشهادة
        if latest_certificate and latest_certificate.education_degree_type:
            return latest_certificate
    
        return None  # إرجاع None إذا لم توجد شهادة أو لم يوجد نوع شهادة مرتبط بها
    
    @classmethod
    def get_second_latest_certificate(cls, employee):
    # استعلام لتحميل الشهادات المرتبطة بالموظف مرتبة حسب تاريخ التنفيذ
        certificates = cls.objects.filter(basic_info=employee) \
        .select_related('education_degree_type') \
        .order_by('-effective_time')

    # تحقق من وجود أكثر من شهادة
        if certificates.count() >= 2:
        # إرجاع الشهادة ما قبل الأخيرة
            return certificates[1]  # الشهادة ما قبل الأخيرة (التي تأتي في المركز الثاني)

    # إذا لم يكن هناك سوى شهادة واحدة أو لا توجد شهادات، إرجاع None
        return None

    
    def __str__(self):
        latest_certificate = self.get_latest_certificate(self.basic_info)  # استدعاء الدالة للحصول على أحدث شهادة
        if latest_certificate:
            return f"{self.basic_info} - {self.education_degree_type} (أحدث شهادة: {latest_certificate.education_degree_type}) - (سنوات التاثير : {latest_certificate.education_degree_type.years_effects})"
        return f"{self.basic_info} - {self.education_degree_type} (لا توجد شهادات)"
    


########################### Log ##################
# نموذج سجل تغييرات الشهادات الأكاديمية للموظفين
class EmployeeEducationChangeLog(models.Model):
    employee_education = models.ForeignKey(
        EmployeeEducation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الشهادة الأكاديمية")
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
        verbose_name = _("سجل تغييرات الشهادات الأكاديمية")
        verbose_name_plural = _("سجلات تغييرات الشهادات الأكاديمية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_education} - {self.action} - {self.timestamp}"


############## Signal ##################

# الإشارات (Signals) الخاصة بـ EmployeeEducation
@receiver(pre_save, sender=EmployeeEducation)
def log_employee_education_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeEducation.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeEducationChangeLog.objects.create(
                employee_education=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmployeeEducation)
def log_employee_education_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeEducationChangeLog.objects.create(
            employee_education=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmployeeEducation)
def log_employee_education_deletion(sender, instance, **kwargs):
    EmployeeEducationChangeLog.objects.create(
        employee_education=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )