from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
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
from django.db.models.signals import pre_save, post_save, pre_delete
from collections import defaultdict
from .hr_utilities_models import DutyAssignmentOrder, PlaceOfEmployment
from django.core.exceptions import ValidationError
from django.utils.text import slugify



class PayrollBudgetType(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payroll_budget_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )
    name_in_arabic = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم نوع الموازنة  بالعربية"),
        help_text=_("يرجى إدخال اسم اسم نوع الموازنة بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("اسم نوع الموازنة  بالانكليزية"),
        help_text=_("يرجى إدخال اسم نوع الموازنة بالانكليزية.")
    )
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")
    
    commennts = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن  نوع الموازنة  "),
        help_text=_("ملاحظات عن نوع الموازنة   ")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم نوع الملاك (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('نوع  الموازنة  ')
        verbose_name_plural = _('انواع  الموازنات  ')
        permissions = [
            ("can_add_payroll_budget_type", "يمكن إضافة نوع موازنة"),
            ("can_update_payroll_budget_type", "يمكن تحديث نوع الموازنة"),
            ("can_delete_payroll_budget_type", "يمكن حذف نوع الموازنة"),
            ("can_view_payroll_budget_type", "يمكن عرض نوع الموازنة"),
        ]
    
    def get_description(self):
        return "يتعامل هذا الجدول مع نوع الموازنة من حيث تشغيلية او استثمارية او نوع جديد بالمستقبل , من خلال اضافة او تحديث او حذف الاسم ."

    def save(self, *args, **kwargs):
        
        if self.is_default:
            PayrollBudgetType.objects.exclude(pk=self.pk).update(is_default=False)
        
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))
            original_slug = self.slug
            counter = 1
            while PayrollBudgetType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

                
        # استدعاء دالة save الأصلية
        super(PayrollBudgetType, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name_in_arabic}"
    



class StaffStructerType(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='staff_structer_Type_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )
    name_in_arabic = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم نوع الملاك  بالعربية"),
        help_text=_("يرجى إدخال اسم اسم نوع الملاك بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("اسم نوع الملاك  بالانكليزية"),
        help_text=_("يرجى إدخال اسم نوع الملاك بالانكليزية.")
    )
    payroll_budget_type = models.ForeignKey(
        PayrollBudgetType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payroll_budget_type_created_by',
        help_text=_("يرجى اختيار اسم الموازنة .")
    )
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")

    is_basic_info_effect = models.BooleanField(default=False,
                                                verbose_name="هل له تاثير انفكاك",
                                                help_text="يرجى تحديد فيما اذا كان هذا النوع من الملاك له تاثير  على دخول الموظف للنظام")

    commennts = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن  الملاك  "),
        help_text=_("ملاحظات عامة عن الملاك ان وجدت   ")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم نوع الملاك (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('نوع  الملاك  ')
        verbose_name_plural = _('انواع  الملاك  ')
        permissions = [
            ("can_add_staff_structer_type", "يمكن إضافة نوع ملاك"),
            ("can_update_staff_structer_type", "يمكن تحديث نوع الملاك"),
            ("can_delete_staff_structer_type", "يمكن حذف نوع الملاك"),
            ("can_view_staff_structer_type", "يمكن عرض نوع الملاك"),
        ]
    def get_description(self):
        return "يتعامل هذا الجدول مع اسم نوع الملاك  من حيث إضافة  جديدة أو تحديث اسم  موجود أو حذفه."

    def save(self, *args, **kwargs):
        if self.payroll_budget_type is None:
            try:
                self.payroll_budget_type = PayrollBudgetType.objects.get(is_default=True)
            except PayrollBudgetType.DoesNotExist:
                raise ValidationError(_("لا يوجد نوع موازنة افتراضي. يرجى إنشاء واحد قبل المتابعة."))

        if self.is_default:
            # إذا كان هناك سجل آخر هو الافتراضي، امنع الحفظ
            existing_default = StaffStructerType.objects.filter(is_default=True).exclude(id=self.id).exists()
            if existing_default:
                raise ValidationError(_("لا يمكن تعيين أكثر من نوع موازنة كافتراضي."))

        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while StaffStructerType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(StaffStructerType, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية
    def __str__(self):
        return f"{self.name_in_arabic}"



class EmployeeStaffKind(models.Model):
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_staff_type_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات.")
    )

    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employee_staff_kind',
        verbose_name=_("رقم الموظف"),
        help_text=_("اختر الموظف المرتبط بهذه الوثيقة.")
    )

    employee_staff_type = models.ForeignKey(
        StaffStructerType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_structure',
        verbose_name=_("نوع الملاك"),
        help_text=_("اختر نوع الملاك المرتبط بهذا الموظف.")
    )

    employee_staff_type_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        help_text=_("الرقم الإداري.")
    )

    employee_staff_type_number_date = models.DateField(null=True, blank=True, help_text=_("تاريخ صدور الامر (اختياري)."))
    
    pdf_file = models.FileField(
        upload_to='Staff/staff_file/',
        null=True,
        blank=True,
        verbose_name="   ملف الامر الخاص بهذا الموظف -اختياري",
        help_text="قم برفع ملف pdf الخاص بالموظف"
    )
    
    comments = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات"),
        help_text=_("يرجى إدخال ملاحظات عن الموظف ان وجدت.")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم الشهادة (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('الملاك ')
        verbose_name_plural = _('الملاك ')
        permissions = [
            ("can_add_employee_staff_kind", "يمكن اضافة الموظف الى الملاك "),
            ("can_update_employee_staff_kind", "يمكن تحديث نوع الموظف من حيث الملاك"),
            ("can_delete_employee_staff_kind", "يمكن حذف نوع الموظف من حيث الملاك"),
            ("can_view_employee_staff_kind", "يمكن عرض نوع الموظف من حيث الملاك"),
        ]
    
    def get_description(self):
        return "يتعامل هذا الجدول مع الملاك للموظفين من حيث إضافة جديدة أو تحديث اسم موجود أو حذفه."
    
    def save(self, *args, **kwargs):
        if self.employee_staff_type and self.employee_staff_type.is_basic_info_effect:
        # تحديث is_approved في BasicInfo
            basic_info_instance = self.basic_info
            if basic_info_instance:
                basic_info_instance.is_approved = False
                basic_info_instance.save()


        if not self.employee_staff_type:
            default_type = StaffStructerType.objects.filter(is_default=True).first()
            if default_type:
                self.employee_staff_type = default_type
            else:
                raise ValidationError(_("لا يوجد نوع ملاك افتراضي. يرجى تعيين نوع افتراضي أولًا."))
    
        
        if not self.slug and self.basic_info:
            # التأكد من الحقول
            employee_name = self.basic_info.firstname if self.basic_info.firstname else "unknown"
            # إنشاء base_slug باستخدام بيانات مختصرة
            base_slug = f"{self.basic_info.secondname}-{employee_name[:4]}"
            base_slug = slugify(unidecode(base_slug))

            # التأكد من تفرد slug
            original_slug = base_slug
            counter = 1
            while EmployeeStaffKind.objects.filter(slug=base_slug).exists():
                base_slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = base_slug

        super(EmployeeStaffKind, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.basic_info.get_full_name()}"  # استدعاء الدالة save الأصلية



##################################### Log #########################

class PayrollBudgetTypeChangeLog(models.Model):
    payroll_budget_type = models.ForeignKey(
        PayrollBudgetType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع الموازنة")
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
        verbose_name = _("سجل تغييرات نوع الموازنة")
        verbose_name_plural = _("سجلات تغييرات أنواع الموازنات")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.payroll_budget_type} - {self.action} - {self.timestamp}"


class StaffStructerTypeChangeLog(models.Model):
    staff_structer_type = models.ForeignKey(
        StaffStructerType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع الملاك")
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
        verbose_name = _("سجل تغييرات نوع الملاك")
        verbose_name_plural = _("سجلات تغييرات أنواع الملاك")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.staff_structer_type} - {self.action} - {self.timestamp}"
    

class EmployeeStaffKindChangeLog(models.Model):
    employee_staff_kind = models.ForeignKey(
        EmployeeStaffKind,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع الملاك")
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
        verbose_name = _("سجل تغييرات الموظف والملاك")
        verbose_name_plural = _("سجلات تغييرات الموظفين والملاك")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_staff_kind} - {self.action} - {self.timestamp}"


#################################### Signal ###############################
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=PayrollBudgetType)
def log_payroll_budget_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = PayrollBudgetType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            PayrollBudgetTypeChangeLog.objects.create(
                payroll_budget_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=PayrollBudgetType)
def log_payroll_budget_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        PayrollBudgetTypeChangeLog.objects.create(
            payroll_budget_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=PayrollBudgetType)
def log_payroll_budget_type_deletion(sender, instance, **kwargs):
    PayrollBudgetTypeChangeLog.objects.create(
        payroll_budget_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


######################## Signal ####################

@receiver(pre_save, sender=StaffStructerType)
def log_staff_structer_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = StaffStructerType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            StaffStructerTypeChangeLog.objects.create(
                staff_structer_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=StaffStructerType)
def log_staff_structer_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        StaffStructerTypeChangeLog.objects.create(
            staff_structer_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=StaffStructerType)
def log_staff_structer_type_deletion(sender, instance, **kwargs):
    StaffStructerTypeChangeLog.objects.create(
        staff_structer_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )

@receiver(pre_save, sender=EmployeeStaffKind)
def log_employee_staff_kind_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeStaffKind.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeStaffKindChangeLog.objects.create(
                employee_staff_kind=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeStaffKind)
def log_employee_staff_kind_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeStaffKindChangeLog.objects.create(
            employee_staff_kind=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=EmployeeStaffKind)
def log_employee_staff_kind_deletion(sender, instance, **kwargs):
    EmployeeStaffKindChangeLog.objects.create(
        employee_staff_kind=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )
