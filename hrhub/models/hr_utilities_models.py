from django.db import models
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey
from accounts.models import Employee
from personalinfo.models import BasicInfo
from unidecode import unidecode
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar
import time
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from collections import defaultdict
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن






class DutyAssignmentOrder(models.Model):
    created_by = models.ForeignKey(
        Employee,  # استبدل 'Employee' بالنموذج الصحيح إذا كان في تطبيق مختلف
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duty_assignment_order',
        verbose_name=_("موظف ادخل الامر"),
        help_text=_("الموظف الذي قام بإنشاء هذه المعلومات الخاصة بالاوامر الادارية.")
    )
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم الامر بالعربية"),
        help_text=_("يرجى إدخال اسم الامر بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("اسم الامر بالعربية"),
        help_text=_("يرجى إدخال اسم الامر بالعربية.")
    )
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('معلومات الاوامر ')
        verbose_name_plural = _('معلومات الاوامر')

    def get_description(self):
        return "يتعامل هذا الجدول مع اسماء وانواع الاوامر من حيث إضافة امر جديدة أو تحديث اسم امر موجود أو حذفه."

    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while DutyAssignmentOrder.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(DutyAssignmentOrder, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية

    def __str__(self):
        return self.name_in_arabic
    



class PlaceOfEmployment(MPTTModel):
    name_in_arabic = models.CharField(max_length=255, unique=True,verbose_name="عنوان المؤسسة")
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_titles',
        verbose_name="عنوان المؤسسسة الأعلى"
    )
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")
    description = models.TextField(blank=True, verbose_name="وصف الوظيفة")
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))

    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='Place_Of_Employment_created_by',
        help_text=_("المستخدم الذي قام بإنشاء أو تحديث هذه المعلومات.")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['name_in_arabic']
    def __str__(self):
        return self.name_in_arabic

    class Meta:
        ordering = ['created_at']
        verbose_name = "عنوان المؤسسة او الوزارة "
        verbose_name_plural = "عناوين المؤسسات او الوزارات "

    def get_description(self):
        return _("هذا يهتم بالمؤسسات الرسمية وادخال البيانات وتحديثها وحذفها  ")
    
    def save(self, *args, **kwargs):
        if self.is_default:
        # تحقق من وجود سجل آخر بقيمة is_default = True
            if PlaceOfEmployment.objects.filter(is_default=True).exclude(pk=self.pk).exists():
                raise ValueError(_("لا يمكن أن يكون هناك أكثر من سجل واحد يحمل القيمة الافتراضية."))
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام title_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while PlaceOfEmployment.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(PlaceOfEmployment, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية



############################### Log #######################

# نموذج سجل تغييرات أوامر التكليف
class DutyAssignmentOrderChangeLog(models.Model):
    duty_assignment_order = models.ForeignKey(
        DutyAssignmentOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الأمر الإداري")
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
        verbose_name = _("سجل تغييرات أوامر التكليف")
        verbose_name_plural = _("سجلات تغييرات أوامر التكليف")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.duty_assignment_order} - {self.action} - {self.timestamp}"




# نموذج سجل تغييرات أماكن التوظيف
class PlaceOfEmploymentChangeLog(models.Model):
    place_of_employment = models.ForeignKey(
        PlaceOfEmployment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("مكان التوظيف")
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
        verbose_name = _("سجل تغييرات أماكن التوظيف")
        verbose_name_plural = _("سجلات تغييرات أماكن التوظيف")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.place_of_employment} - {self.action} - {self.timestamp}"


##################### Singal ####################

# الإشارات (Signals) الخاصة بـ DutyAssignmentOrder
@receiver(pre_save, sender=DutyAssignmentOrder)
def log_duty_assignment_order_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = DutyAssignmentOrder.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            DutyAssignmentOrderChangeLog.objects.create(
                duty_assignment_order=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=DutyAssignmentOrder)
def log_duty_assignment_order_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        DutyAssignmentOrderChangeLog.objects.create(
            duty_assignment_order=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=DutyAssignmentOrder)
def log_duty_assignment_order_deletion(sender, instance, **kwargs):
    DutyAssignmentOrderChangeLog.objects.create(
        duty_assignment_order=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


            ###### Place of employment #######
# الإشارات (Signals) الخاصة بـ PlaceOfEmployment
@receiver(pre_save, sender=PlaceOfEmployment)
def log_place_of_employment_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = PlaceOfEmployment.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            PlaceOfEmploymentChangeLog.objects.create(
                place_of_employment=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=PlaceOfEmployment)
def log_place_of_employment_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        PlaceOfEmploymentChangeLog.objects.create(
            place_of_employment=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=PlaceOfEmployment)
def log_place_of_employment_deletion(sender, instance, **kwargs):
    PlaceOfEmploymentChangeLog.objects.create(
        place_of_employment=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )