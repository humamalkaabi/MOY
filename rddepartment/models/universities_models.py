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



class College(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='college_employment_info',
        verbose_name=_("College "),
        help_text=_("الموظف الذي قام بإنشاء هذه المعلومات الخاصة الكلية.")
    )
    name_in_arabic = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("اسم الكلية باللغة العربية"),
        help_text=_("الرجاء ادخل اسم الكلية باللغة العربية.")
    )
    name_in_english = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("اسم الكلية باللغة الانكليزية"),
        help_text=_("الرجاء ادخل اسم الكلية باللغة الانكليزية.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
        help_text=_("Unique slug for the college, auto-generated if left blank.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the record was created.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when the record was last updated.")
    )

    class Meta:
        verbose_name = _("الكلية")
        verbose_name_plural = _("الكليات")
        ordering = ['name_in_english']
        permissions = [
            ("can_add_college", "يمكن اضافة اسم الكلية"),
            ("can_update_college", "يمكن تحديث اسم الكلية    "),
            ("can_delete_college", "يمكن حذف اسم   الكلية "),
                ]


    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name_in_english):
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        slug_candidate = slugify(self.name_in_english)
        original_slug = slug_candidate
        counter = 1

        while College.objects.filter(slug=slug_candidate).exists():
            slug_candidate = f"{original_slug}-{counter}"
            counter += 1

        return slug_candidate

    def __str__(self):
        return f"College: {self.name_in_arabic}"



class ForeignUniversity(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='university_employment_info',
        verbose_name=_("Foreign University"),
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الخاصة بالجامعة الأجنبية.")
    )
    name_in_english = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("اسم الجامعة الأجنبية باللغة الإنجليزية"),
        help_text=_("يرجى إدخال اسم الجامعة باللغة الإنجليزية.")
    )
    name_in_arabic = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_("اسم الجامعة الأجنبية باللغة العربية"),
        help_text=_("يرجى إدخال اسم الجامعة باللغة العربية.")
    )
    university_name_abbreviation = models.CharField(
        max_length=10,
        blank=True,
        default='',
        verbose_name=_("مختصر اسم الجامعة"),
        help_text=_("يرجى إدخال مختصر اسم الجامعة باللغة الانكليزية - اختياري.")
    )
    university_link = models.URLField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_("الرابط الإلكتروني للجامعة"),
        help_text=_("يرجى ادخال رابط موقع الجامعة -اختياري - مثل  https://www.example.com")
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True,
        verbose_name=_("Slug"),
        help_text=_("معرف فريد للجامعة، يتم إنشاؤه تلقائيًا إذا تم تركه فارغًا.")
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='universities',
        verbose_name=_("بلد الجامعة"),
        help_text=_("الرجاء اختيار اسم بلد الجامعة.")
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

    class Meta:
        verbose_name = _("الجامعة الأجنبية")
        verbose_name_plural = _("الجامعات الأجنبية")
        ordering = ['name_in_english']
        constraints = [
            models.UniqueConstraint(fields=['name_in_english', 'country'], name='unique_university_per_country')
        ]
        permissions = [
                ("can_add_foreign_university", "يمكن إضافة   اسم جامعة اجنبية"),
                ("can_update_foreign_university", "يمكن تحديث اسم جامعة اجنبية "),
                ("can_delete_foreign_university", "يمكن حذف اسم جامعة اجنبية  "),
            ]

    def save(self, *args, **kwargs):
        if not self.pk or not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        slug_candidate = slugify(self.name_in_english)
        original_slug = slug_candidate
        counter = 1

        while ForeignUniversity.objects.filter(slug=slug_candidate).exists():
            slug_candidate = f"{original_slug}-{counter}"
            counter += 1

        return slug_candidate

    def __str__(self):
        return self.name_in_english
    


class IraqiUniversity(models.Model):
    GOVERNMENTAL = 'governmental'
    PRIVATE = 'private'

    UNIVERSITY_TYPE_CHOICES = [
        (GOVERNMENTAL, _("جامعة حكومية")),  # "جامعة حكومية" بالعربية
        (PRIVATE, _("جامعة أهلية")),  # "جامعة أهلية" بالعربية
    ]


    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='iraqi_university_employment_info',
        verbose_name=_("Iraqi University "),
        help_text=_("الموظف الذي قام بإنشاء هذه المعلومات الخاصة بالجامعة العراقية.")
    )
    name_in_arabic = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("   اسم الجامعة باللغة العربية"),
        help_text=_("ادخل اسم الجامعة بالعربي.")
    )
    name_in_english = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("اسم الجامعة باللغة الانكليزية"),
        help_text=_(" يرجى ادخال اسم الجامعة باللغة الانكليزية.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
        help_text=_("Unique slug for the university, auto-generated if left blank.")
    )
    university_type = models.CharField(
        max_length=50,
        choices=UNIVERSITY_TYPE_CHOICES,
        default=GOVERNMENTAL,
        verbose_name=_("جامعة حكومية ام اهلية"),
        help_text=_("يرجى اختيار هل الجامعة حكومية ام اهلية.")
    )

    governorate = models.ForeignKey(
        Governorate,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='universities',
        verbose_name=_("محافطة"),
        help_text=_("     يرجى ادخال اسم المحافظة الموجودة فيها الجامعة .")
    )
    address = models.TextField(
        verbose_name=_("عنوان الجامعة"),
         blank=True,
        null=True,
        help_text=_("يرجى ادخال عنوان الجامعة (اختياري).")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the record was created.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when the record was last updated.")
    )

    class Meta:
        verbose_name = _("Iraqi University")
        verbose_name_plural = _("Iraqi Universities")
        ordering = ['name_in_arabic']
        constraints = [
            models.UniqueConstraint(fields=['name_in_arabic', 'governorate'], name='unique_iraqi_university_per_governorate')
        ]
        permissions = [
                ("can_add_iraqi_university", "يمكن إضافة   اسم جامعة عراقية"),
                ("can_update_iraqi_university", "يمكن تحديث اسم جامعة عراقية "),
                ("can_delete_iraqi_university", "يمكن حذف اسم جامعة عراقية  "),
            ]


    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(unidecode(self.name_in_arabic)):
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def get_description(self):
        return "يتعامل هذا الجدول مع اسماء الجامعات العراقية والمعلومات الخاصة بها من الاسم او نوع الجامعة او مكان الجامعة   ."

    def generate_unique_slug(self):
        slug_candidate = slugify(unidecode(self.name_in_arabic))
        original_slug = slug_candidate
        counter = 1

        while IraqiUniversity.objects.filter(slug=slug_candidate).exists():
            slug_candidate = f"{original_slug}-{counter}"
            counter += 1

        return slug_candidate

    def __str__(self):
        return self.name_in_arabic




################################# Log  #####################

# نموذج سجل تغييرات الكليات
class CollegeChangeLog(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الكلية")
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
        verbose_name = _("سجل تغييرات الكلية")
        verbose_name_plural = _("سجلات تغييرات الكليات")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.college} - {self.action} - {self.timestamp}"

# نموذج سجل تغييرات الجامعات الأجنبية
class ForeignUniversityChangeLog(models.Model):
    foreign_university = models.ForeignKey(
        ForeignUniversity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الجامعة الأجنبية")
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
        verbose_name = _("سجل تغييرات الجامعة الأجنبية")
        verbose_name_plural = _("سجلات تغييرات الجامعات الأجنبية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.foreign_university} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات الجامعات العراقية
class IraqiUniversityChangeLog(models.Model):
    iraqi_university = models.ForeignKey(
        IraqiUniversity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الجامعة العراقية")
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
        verbose_name = _("سجل تغييرات الجامعة العراقية")
        verbose_name_plural = _("سجلات تغييرات الجامعات العراقية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.iraqi_university} - {self.action} - {self.timestamp}"




########################### Signals #####################
            ###### Signals- College ###########
# الإشارات (Signals) الخاصة بـ College
@receiver(pre_save, sender=College)
def log_college_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = College.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            CollegeChangeLog.objects.create(
                college=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=College)
def log_college_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        CollegeChangeLog.objects.create(
            college=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=College)
def log_college_deletion(sender, instance, **kwargs):
    CollegeChangeLog.objects.create(
        college=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


                #######
# الإشارات (Signals) الخاصة بـ ForeignUniversity
@receiver(pre_save, sender=ForeignUniversity)
def log_foreign_university_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = ForeignUniversity.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            ForeignUniversityChangeLog.objects.create(
                foreign_university=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=ForeignUniversity)
def log_foreign_university_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        ForeignUniversityChangeLog.objects.create(
            foreign_university=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=ForeignUniversity)
def log_foreign_university_deletion(sender, instance, **kwargs):
    ForeignUniversityChangeLog.objects.create(
        foreign_university=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


# الإشارات (Signals) الخاصة بـ IraqiUniversity
@receiver(pre_save, sender=IraqiUniversity)
def log_iraqi_university_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = IraqiUniversity.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            IraqiUniversityChangeLog.objects.create(
                iraqi_university=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=IraqiUniversity)
def log_iraqi_university_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        IraqiUniversityChangeLog.objects.create(
            iraqi_university=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=IraqiUniversity)
def log_iraqi_university_deletion(sender, instance, **kwargs):
    IraqiUniversityChangeLog.objects.create(
        iraqi_university=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )