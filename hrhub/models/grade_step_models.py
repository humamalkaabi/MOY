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
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن



class EmployeeGrade(models.Model):
    grade_number = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1, message="الدرجة يجب أن تكون 1 أو أعلى"),
            MaxValueValidator(10, message="الدرجة يجب أن تكون 10 أو أقل")
        ],
        help_text="رقم الدرجة الوظيفية (1 إلى 10)"
    )
    name_in_words = models.CharField(max_length=50, help_text="اسم الدرجة كتابة")
    
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_grade',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على ادخال البيانات.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("الطابع الزمني عند إنشاء البيانات.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("آخر تحديث"),
        help_text=_("الطابع الزمني عند آخر تحديث للبيانات.")
    )
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug")
    class Meta:
        # unique_together = ('basic_info', 'office', 'position', 'is_primary', 'start_date')
        ordering = ['-grade_number']
        verbose_name = _("الدرجة الوظيفية")
        verbose_name_plural = _("   الدرجات الوظيفية")
        permissions = [
           
    ("can_add_grade", "يمكن اضافة اسم ونوع درجة وظيفية"),
    ("can_update_grade", "يمكن تحديث اسم ونوع الدرجة الوظيفية "),
    ("can_delete_grade", "يمكن حذف الدرجة الوظيفية"),
   ]
    

    def get_description(self):
        return _(" يهتم هذا الجدول باسماء الدرجات الوظيفية")

    
    def get_next_grade(self):
        """
        دالة لإرجاع الدرجة التالية بناءً على التسلسل التنازلي.
        """
        if self.grade_number > 1:  # إذا كانت الدرجة الحالية ليست الدرجة الأولى
            return EmployeeGrade.objects.filter(name=self.grade_number - 1).first()
        return None  # إذا كان في الدرجة الأولى، لا يوجد درجة أعلى
    
    def __str__(self):
        return f"Employee Grade {self.grade_number} - {self.name_in_words}"
    
    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_words و grade_number
        if not self.slug and self.grade_number:
            self.slug = slugify(unidecode(f"{self.name_in_words}-{self.grade_number}"))

        # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while EmployeeGrade.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super(EmployeeGrade, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية




class EmployeeStep(models.Model):
    grade_number = models.ForeignKey(EmployeeGrade, on_delete=models.CASCADE, related_name="steps")
    step_number = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="رقم المرحلة يجب أن يكون 1 أو أعلى"),
            MaxValueValidator(11, message="رقم المرحلة يجب أن يكون 11 أو أقل")
        ],
        help_text="رقم المرحلة الوظيفية (1 إلى 11)"
    )
    name_in_words = models.CharField(max_length=50, help_text="اسم المرحلة كتابة")
    
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_step',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على ادخال البيانات.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("الطابع الزمني عند إنشاء البيانات.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("آخر تحديث"),
        help_text=_("الطابع الزمني عند آخر تحديث للبيانات.")
    )
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug")

    class Meta:
        unique_together = ('grade_number', 'step_number')  # لا تتكرر نفس المرحلة داخل الدرجة
        ordering = ['grade_number', 'step_number']  # ترتيب المراحل حسب الدرجة ثم المرحلة
        verbose_name = _("المرحلة الوظيفية")
        verbose_name_plural = _("   المراحل الوظيفية")
        permissions = [
            ("can_add_step", "يمكن اضافة اسم ونوع المرحلة وظيفية"),
            ("can_update_step", "يمكن تحديث اسم ونوع المرحلة الوظيفية "),
            ("can_delete_step", "يمكن حذف المرحلة الوظيفية"),
   ]


    def save(self, *args, **kwargs):
        if not self.slug and self.step_number:
            # تكوين النص المطلوب لإنشاء الـ slug
            self.slug = slugify(unidecode(f"{self.grade_number.grade_number}-{self.step_number}-{self.name_in_words}"))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while EmployeeStep.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super(EmployeeStep, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية


    def __str__(self):
        return f"الدرجة الوظيفة {self.grade_number.grade_number} - المرحلة {self.step_number}"


################################ Logs ##########################

# نموذج سجل تغييرات الدرجات الوظيفية
class EmployeeGradeChangeLog(models.Model):
    employee_grade = models.ForeignKey(
        EmployeeGrade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الدرجة الوظيفية")
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
        verbose_name = _("سجل تغييرات الدرجة الوظيفية")
        verbose_name_plural = _("سجلات تغييرات الدرجات الوظيفية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_grade} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات المراحل الوظيفية
class EmployeeStepChangeLog(models.Model):
    employee_step = models.ForeignKey(
        EmployeeStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("المرحلة الوظيفية")
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
        verbose_name = _("سجل تغييرات المرحلة الوظيفية")
        verbose_name_plural = _("سجلات تغييرات المراحل الوظيفية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_step} - {self.action} - {self.timestamp}"



########################### Signals ###############################

        #### Signals - EmployeeGrade

# الإشارات (Signals) الخاصة بـ EmployeeGrade
@receiver(pre_save, sender=EmployeeGrade)
def log_employee_grade_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeGrade.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeGradeChangeLog.objects.create(
                employee_grade=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmployeeGrade)
def log_employee_grade_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeGradeChangeLog.objects.create(
            employee_grade=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmployeeGrade)
def log_employee_grade_deletion(sender, instance, **kwargs):
    EmployeeGradeChangeLog.objects.create(
        employee_grade=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



# الإشارات (Signals) الخاصة بـ EmployeeStep
@receiver(pre_save, sender=EmployeeStep)
def log_employee_step_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeStep.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeStepChangeLog.objects.create(
                employee_step=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmployeeStep)
def log_employee_step_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeStepChangeLog.objects.create(
            employee_step=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmployeeStep)
def log_employee_step_deletion(sender, instance, **kwargs):
    EmployeeStepChangeLog.objects.create(
        employee_step=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )