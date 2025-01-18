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
import threading
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from collections import defaultdict
from .hr_utilities_models import DutyAssignmentOrder
from .office_position_models import EmployeeOfficePosition, Position, Office
from .employement_models import EmploymentHistory
from rddepartment.models.employee_education_models import EmployeeEducation
from locations.models import Governorate





class CentralFinancialAllocationsType(models.Model):
    
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='central_financial_allocations_type_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم المخصصات  بالعربية"),
        help_text=_("يرجى إدخال اسم المخصصات بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("اسم المخصصات بالانكليزية "),
        help_text=_("يرجى إدخال اسم المخصصات بالانكليزية -اختياري- .")
    )
    ratio = models.PositiveIntegerField(
        null=True, blank=True, 
        verbose_name=_("نسبة المخصصات رقما "),
         help_text=_("يرجى ادخال نسبة المخصصات رقما - اختياري-")
    )
    word_ratio =  models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("نسبة المخصصات كتابة "),
         help_text=_("يرجى ادخال نسبة المخصصات كتابة - اختياري-")
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن هذا النوع من المخصصات"),
        help_text=_("ملاحظات عامة عن هذا النوع من المخصصات - اختياري -")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه لنوع المخصصات  (يتم إنشاؤه تلقائيًا)."))
    class Meta:
        verbose_name = "نوع المخصصات المالية المركزية"
        verbose_name_plural = "أنواع المخصصات المالية المركزية"
        permissions = [
            ("can_add_central_financial_allocations_type", "يمكن اضافة نوع مخصصات "),
            ("can_update_central_financial_allocations_type", "يمكن تحديث نوع  المخصصات"),
            ("can_delete_central_financial_allocations_type", "يمكن حذف نوع المخصصات   "),
            ("can_view_central_financial_allocations_type", "يمكن عرض نوع نوع المخصصات "),
        ]



    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام title_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while CentralFinancialAllocationsType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(CentralFinancialAllocationsType, self).save(*args, **kwargs)

    def get_description(self):
        return "يتعامل هذا الجدول مع  نوع واسم المخصصات المركزية من حيث إضافة جديدة أو تحديث اسم موجود أو حذفه."
    def __str__(self):
        return self.name_in_arabic if self.name_in_arabic else _("بدون اسم")
    


class CentralFinancialAllocations(models.Model):
    basic_info = models.ForeignKey(BasicInfo, 
                                   on_delete=models.CASCADE, 
                                   related_name="allocations")
    
    
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='central_financial_allocations_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )
    centralfinancialallocationstype = models.ForeignKey(
        CentralFinancialAllocationsType,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='centralfinancialallocationstype',
        help_text=_("يرجى اختيار نوع المخصصات")
    )
    order_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_(" الامر الصادر    "),
        help_text=_("    يرجى ادخال الامر الصادر ")

    )
    order_time = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("تاريخ صدور الامر"),
        help_text=_("ادخل تاريخ صدور الامر")
    )
    effective_time = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("تاريخ تنفيذ الامر"),
        help_text=_("أدخل تاريخ  تنفيذ الامر   .")
    )

    serial_namber =  models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("   رقم السيريال الخاص بالكومبيوتر   "),
        help_text=_("    يرجى ادخال رقم السيريال الخاص بالكومبيوتر -اختياري-  ")
    )
    mac_namber =  models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("   رقم mac_namber     "),
        help_text=_("    يرجى ادخال رقم mac_namber  ")
    )
   
    
    residency = models.ForeignKey(
        Governorate,
         on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='emp_residency',
        verbose_name=_(" محافظة سكن الموظف  "),
        help_text=_("     يرجى ادخال محافظة سكن الموظف   .")

    )

    address =  models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_(" عنوان سكن الموظف  "),
        help_text=_("   يرجى ادخال عنوان سكن الموظف  ")
    )

    vechile_name =  models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_(" اسم العجلة    "),
        help_text=_("    ادخل اسم العجلة في حالة مخصصات خطورة السواق ")
    )
    vechile_number =  models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_(" رقم العجلة    "),
        help_text=_("    ادخل رقم العجلة في حالة مخصصات خطورة السواق ")
    )
    vechile_line =  models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_(" صفة الخطورة ومكان الخط     "),
        help_text=_("    ادخل صفحة الخطورة ومكان الخط       ")
    )
    healthy_cen = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("نوع المخصصات الصحية       "),
        help_text=_(" يرجى ادخال اسم المخصصات الصحية     ")
    )
    name_prevois = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("اسم البديل السابق     "),
        help_text=_(" يرجى ادخال اسم البديل السابق    ")
    )

    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("ملاحظات  المخصصات المركزية للموظف"),
        help_text=_("ملاحظات عامة عن هذا المخصصات المركزية للموظف  - اختياري -")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم الشهادة (يتم إنشاؤه تلقائيًا)."))
    class Meta:
        verbose_name = "مخصصات الموظف   "
        verbose_name_plural = "المخصصات المركزية   "
        permissions = [
            ("can_add_central_financial_allocations", "يمكن اضافة  مخصصات مركزية للموظف "),
            ("can_update_central_financial_allocations", "يمكن تحديث   المخصصات المركزية للموظف"),
            ("can_delete_central_financial_allocations", "يمكن حذف  المخصصات المركزية للموظف   "),
            ("can_view_central_financial_allocations", "يمكن عرض نوع  المخصصات المركزية للموظف "),
        ]

    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام title_in_arabic
        if not self.slug and self.basic_info:
            self.slug = slugify(unidecode(self.basic_info.firstname))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while CentralFinancialAllocations.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(CentralFinancialAllocations, self).save(*args, **kwargs)

    def get_description(self):
        return "يتعامل هذا الجدول مع  المخصصات الهندسية للموظفين من حيث إضافة جديدة أو تحديث اسم موجود أو حذفه."








############################## Log ###############################
class CentralFinancialAllocationsTypeChangeLog(models.Model):
    central_financial_allocation_type = models.ForeignKey(
        CentralFinancialAllocationsType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع المخصص المالي المركزي")
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
        verbose_name = _("سجل تغييرات نوع المخصص المالي المركزي")
        verbose_name_plural = _("سجلات تغييرات أنواع المخصصات المالية المركزية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.central_financial_allocation_type} - {self.action} - {self.timestamp}"


class CentralFinancialAllocationsChangeLog(models.Model):
    allocation = models.ForeignKey(
        CentralFinancialAllocations,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("مخصص الموظف")
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
        verbose_name = _("سجل تغييرات المخصصات المركزية")
        verbose_name_plural = _("سجلات تغييرات المخصصات المركزية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.allocation} - {self.action} - {self.timestamp}"

###################### Signal ######################

# تتبع التعديلات
@receiver(pre_save, sender=CentralFinancialAllocationsType)
def log_central_financial_allocations_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = CentralFinancialAllocationsType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            CentralFinancialAllocationsTypeChangeLog.objects.create(
                central_financial_allocation_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )
# تتبع الإضافات
@receiver(post_save, sender=CentralFinancialAllocationsType)
def log_central_financial_allocations_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        CentralFinancialAllocationsTypeChangeLog.objects.create(
            central_financial_allocation_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


# تتبع الحذف
@receiver(post_delete, sender=CentralFinancialAllocationsType)
def log_central_financial_allocations_type_deletion(sender, instance, **kwargs):
    CentralFinancialAllocationsTypeChangeLog.objects.create(
        central_financial_allocation_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )




@receiver(pre_save, sender=CentralFinancialAllocations)
def log_central_financial_allocations_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = CentralFinancialAllocations.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            CentralFinancialAllocationsChangeLog.objects.create(
                allocation=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=CentralFinancialAllocations)
def log_central_financial_allocations_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        CentralFinancialAllocationsChangeLog.objects.create(
            allocation=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=CentralFinancialAllocations)
def log_central_financial_allocations_deletion(sender, instance, **kwargs):
    CentralFinancialAllocationsChangeLog.objects.create(
        allocation=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )
