from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from personalinfo.models import BasicInfo
from locations.models import Country, Governorate
from unidecode import unidecode
from accounts.models import Employee
# Content types
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from mptt.models import MPTTModel, TreeForeignKey
from hrhub.models.grade_step_models import EmployeeGrade, EmployeeStep
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن
from mptt.models import MPTTModel, TreeForeignKey
from datetime import timedelta
from dateutil.relativedelta import relativedelta



class CourseCertificateType(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='course_certificate_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الخاصة بالمدرسة.")
    )
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم الشهادة  بالعربية"),
        help_text=_("يرجى إدخال اسم الشهادة بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("اسم الشهادة  بالانكليزية"),
        help_text=_("يرجى إدخال اسم الشهادة بالانكليزية.")
    )
    is_approved = models.BooleanField(
        default=False, 
        verbose_name=_("هل هي مطلوبة للاغراض الادارية    "), 
        help_text=_("هل يوجد لها تاثير على الامور الادارية مثل الترفع  ")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("تاريخ ووقت إنشاء السجل.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث"),
        help_text=_("تاريخ ووقت آخر تحديث للسجل.")
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Add slug field
    class Meta:
            verbose_name = _("نوع شهادة الدورة")
            verbose_name_plural = _("أنواع شهادات الدورات")
            ordering = ['name_in_arabic']
            permissions = [
                ("can_add_course_certificate_type", "يمكن إضافة نوع شهادة الدورة"),
                ("can_update_course_certificate_type", "يمكن تحديث نوع شهادة الدورة"),
                ("can_delete_course_certificate_type", "يمكن حذف نوع شهادة الدورة"),
            ]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from certificate_name and issue_date
            base_slug = slugify(unidecode(f"{self.name_in_arabic} {self.created_at}"))
            slug = base_slug
            counter = 1
            
            # Ensure uniqueness by checking if slug already exists
            while CourseCertificateType.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_in_arabic
    



class CourseCertificateInstitution(models.Model):  # بدلًا من models.Model
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='course_certificate_institution_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الخاصة بالمدرسة.")
    )

    
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم الشهادة  بالعربية"),
        help_text=_("يرجى إدخال اسم الشهادة بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("اسم الشهادة  بالانكليزية"),
        help_text=_("يرجى إدخال اسم الشهادة بالانكليزية.")
    )
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات ")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("تاريخ ووقت إنشاء السجل.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث"),
        help_text=_("تاريخ ووقت آخر تحديث للسجل.")
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
            verbose_name = _("مؤسسة شهادة الدورة")
            verbose_name_plural = _("مؤسسات شهادات الدورات")
            ordering = ['name_in_arabic']
            constraints = [
                models.UniqueConstraint(
                    fields=['is_default'],
                    condition=models.Q(is_default=True),
                    name='unique_default_course_certificate_institution'
                )]
            permissions = [
                ("can_add_course_certificate_institution", "يمكن إضافة مؤسسة شهادة دورة"),
                ("can_update_course_certificate_institution", "يمكن تحديث مؤسسة شهادة دورة"),
                ("can_delete_course_certificate_institution", "يمكن حذف مؤسسة شهادة دورة"),
            ]

    def save(self, *args, **kwargs):
        if self.is_default:
        # تعطيل جميع السجلات الأخرى من أن تكون افتراضية
            CourseCertificateInstitution.objects.exclude(pk=self.pk).update(is_default=False)

        

        if not self.slug:
            # Generate slug from certificate_name and issue_date
            base_slug = slugify(unidecode(f"{self.name_in_arabic}"))
            slug = base_slug
            counter = 1
            
            # Ensure uniqueness by checking if slug already exists
            while CourseCertificateInstitution.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_in_arabic




class EmployeeCourseCertificate(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employee_course_certificate_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الخاصة بالشهادة.")
    )

    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employee_course_certificate',
        verbose_name=_("رقم الموظف"),
        help_text=_("اختر الموظف المرتبط بهذه الشهادة.")
    )
    coursecertificatetype = models.ForeignKey(
        CourseCertificateType,
        on_delete=models.CASCADE,
        null=True, 
        blank=True, 
        related_name='employee_course_certificate_type',
        verbose_name=_("نوع الشهادة"),
        help_text=_("يرجى اختيار نوع الشهادة.")
    )
    name_of_the_institution = models.ForeignKey(
        CourseCertificateInstitution,
        on_delete=models.CASCADE,
        null=True, 
        blank=True, 
        related_name='employee_course_certificate_institution_name',
        verbose_name=_("اسم المؤسسة المناحة "),
        help_text=_("يرجى اختيار المؤسسة المانحة .")
    )
    course_number= models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("رقم كتاب اصدار الشهادة    "),
        help_text=_("يرجى إدخال   رقم كتاب اصدار الشهادة  .")
    )

    date_issued = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ اصدار الشهادة"),
        help_text=_("أدخل تاريخ إصدار الشهادة.")
    )


    start_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ المباشرة بالدورة "),
        help_text=_("أدخل تاريخ المباشرة بالدورة .")
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ انتهاء الدورة  "),
        help_text=_("أدخل تاريخ انتهاء الدورة  .")
    )
    certificate_file = models.FileField(
        upload_to='coursecertificate/pdfs/',
        verbose_name=_("ملف الشهادة"),
        help_text=_("قم بتحميل ملف PDF الخاص بالشهادة الأكاديمية."),
        null=True,
        blank=True
    )
    course_duration= models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("مدة الدورة   "),
        help_text=_("يرجى إدخال   مدة الدورة.")
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات ")

    slug = models.SlugField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("معرف فريد"),
        help_text=_("معرف فريد.")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التعديل")
    class Meta:
        verbose_name = _("شهادة تدريبية وورش")
        verbose_name_plural = _("الشهادات التدريبية وورش العمل")
        ordering = ['coursecertificatetype', 'date_issued']
        permissions = [
            ("can_add_employee_course_certificate", "يمكن إضافة شهادة تدريبية"),
            ("can_update_employee_course_certificate", "يمكن تحديث شهادة تدريبية"),
            ("can_delete_employee_course_certificate", "يمكن حذف شهادة تدريبية"),
        ]

    
    def save(self, *args, **kwargs):

        if not self.name_of_the_institution:
        # حاول العثور على المؤسسة الافتراضية
            default_institution = CourseCertificateInstitution.objects.filter(is_default=True).first()
            if default_institution:
                self.name_of_the_institution = default_institution

        if not self.course_duration:
            if self.end_date and self.start_date:
                duration_in_days = (self.end_date - self.start_date).days
                self.course_duration = duration_in_days
            else:
                self.course_duration = None

        if not self.slug:
            # أنشئ slug باستخدام بيانات مفيدة
            base_slug = slugify(unidecode(f"{self.basic_info.slug}-{self.coursecertificatetype.name_in_arabic}-{self.date_issued}"))
            slug = base_slug
            counter = 1

            # تحقق من وجود slug مكرر وقم بتعديله إذا لزم الأمر
            while EmployeeCourseCertificate.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        
        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.basic_info.get_full_name()



###################### Logs ######################
# نموذج سجل تغييرات أنواع شهادات الدورات
class CourseCertificateTypeChangeLog(models.Model):
    course_certificate_type = models.ForeignKey(
        CourseCertificateType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع شهادة الدورة")
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
        verbose_name = _("سجل تغييرات نوع شهادة الدورة")
        verbose_name_plural = _("سجلات تغييرات أنواع شهادات الدورات")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.course_certificate_type} - {self.action} - {self.timestamp}"



# نموذج سجل تغييرات مؤسسات شهادات الدورات
# class CourseCertificateInstitutionChangeLog(models.Model):
#     course_certificate_institution = models.ForeignKey(
#         CourseCertificateInstitution,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="change_logs",
#         verbose_name=_("مؤسسة شهادة الدورة")
#     )
#     action = models.CharField(
#         max_length=20,
#         choices=[
#             ('create', 'إضافة'),
#             ('update', 'تعديل'),
#             ('delete', 'حذف'),
#         ],
#         verbose_name=_("نوع العملية")
#     )
#     field_name = models.CharField(
#         max_length=100,
#         null=True,
#         blank=True,
#         verbose_name=_("اسم الحقل")
#     )
#     old_value = models.TextField(
#         null=True,
#         blank=True,
#         verbose_name=_("القيمة القديمة")
#     )
#     new_value = models.TextField(
#         null=True,
#         blank=True,
#         verbose_name=_("القيمة الجديدة")
#     )
#     user = models.ForeignKey(
#         Employee,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("المستخدم المسؤول")
#     )
#     timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

#     class Meta:
#         verbose_name = _("سجل تغييرات مؤسسة شهادة الدورة")
#         verbose_name_plural = _("سجلات تغييرات مؤسسات شهادات الدورات")
#         ordering = ['-timestamp']

#     def __str__(self):
#         return f"{self.course_certificate_institution} - {self.action} - {self.timestamp}"



# نموذج سجل تغييرات شهادات التدريب
class EmployeeCourseCertificateChangeLog(models.Model):
    employee_course_certificate = models.ForeignKey(
        EmployeeCourseCertificate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الشهادة التدريبية")
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
        verbose_name = _("سجل تغييرات الشهادات التدريبية")
        verbose_name_plural = _("سجلات تغييرات الشهادات التدريبية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_course_certificate} - {self.action} - {self.timestamp}"




########################### Signals #################
# الإشارات (Signals) الخاصة بـ CourseCertificateType
@receiver(pre_save, sender=CourseCertificateType)
def log_course_certificate_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = CourseCertificateType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            CourseCertificateTypeChangeLog.objects.create(
                course_certificate_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=CourseCertificateType)
def log_course_certificate_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        CourseCertificateTypeChangeLog.objects.create(
            course_certificate_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=CourseCertificateType)
def log_course_certificate_type_deletion(sender, instance, **kwargs):
    CourseCertificateTypeChangeLog.objects.create(
        course_certificate_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )




# # الإشارات (Signals) الخاصة بـ CourseCertificateInstitution
# @receiver(pre_save, sender=CourseCertificateInstitution)
# def log_course_certificate_institution_changes(sender, instance, **kwargs):
#     if instance.pk:  # إذا كان السجل موجودًا مسبقًا
#         previous = CourseCertificateInstitution.objects.get(pk=instance.pk)
#         changes = []

#         for field in instance._meta.fields:
#             field_name = field.name
#             old_value = getattr(previous, field_name, None)
#             new_value = getattr(instance, field_name, None)

#             if old_value != new_value:
#                 changes.append((field_name, old_value, new_value))

#         for field_name, old_value, new_value in changes:
#             CourseCertificateInstitutionChangeLog.objects.create(
#                 course_certificate_institution=instance,
#                 action="update",
#                 field_name=field_name,
#                 old_value=old_value,
#                 new_value=new_value,
#                 user=instance.created_by,  # المستخدم المسؤول
#             )


# @receiver(post_save, sender=CourseCertificateInstitution)
# def log_course_certificate_institution_creation(sender, instance, created, **kwargs):
#     if created:  # إذا كان السجل جديدًا
#         CourseCertificateInstitutionChangeLog.objects.create(
#             course_certificate_institution=instance,
#             action="create",
#             user=instance.created_by,  # المستخدم المسؤول
#         )


# @receiver(post_delete, sender=CourseCertificateInstitution)
# def log_course_certificate_institution_deletion(sender, instance, **kwargs):
#     CourseCertificateInstitutionChangeLog.objects.create(
#         course_certificate_institution=None,  # السجل المحذوف
#         action="delete",
#         user=instance.created_by,  # المستخدم المسؤول
#     )





# الإشارات (Signals) الخاصة بـ EmployeeCourseCertificate
@receiver(pre_save, sender=EmployeeCourseCertificate)
def log_employee_course_certificate_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeCourseCertificate.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeCourseCertificateChangeLog.objects.create(
                employee_course_certificate=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmployeeCourseCertificate)
def log_employee_course_certificate_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeCourseCertificateChangeLog.objects.create(
            employee_course_certificate=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmployeeCourseCertificate)
def log_employee_course_certificate_deletion(sender, instance, **kwargs):
    EmployeeCourseCertificateChangeLog.objects.create(
        employee_course_certificate=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )