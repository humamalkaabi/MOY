import os
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
import threading
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from collections import defaultdict
from .hr_utilities_models import PlaceOfEmployment
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن



def employement_type_pdf_path(instance, filename):
    # استخدام اسم النوع (name) مع عنوان "EmployementType"
    employement_type_name = instance.name if instance.name else "unknown"
    
    # بناء المسار
    return f"employement_type_pdfs/EmployementType/{employement_type_name}/{filename}"

class EmployementType(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")

    is_employment_type_counted = models.BooleanField(
            default=True, 
        verbose_name=_("يُحسب ضمن التوظيف")
        )

   
    pdf_file = models.FileField(
        upload_to=employement_type_pdf_path,
        blank=True,
        null=True,
        verbose_name="ملف PDF",
        help_text="السند القانوني لهذا النوع من التوظيف اختياري     "
    )
    comments = models.CharField(max_length=255,
                                  blank=True, null=True,
                                   help_text=_(" ملاحظات."))  # اسم الإجازة
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_Employement_Type',
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
        verbose_name = _("نوع التوظيف")
        verbose_name_plural = _("انواع التوظيف")
        constraints = [
            models.UniqueConstraint(
                fields=['is_default'],
                condition=models.Q(is_default=True),
                name="unique_default_employment_type"
            )
        ]
        permissions = [
            ("can_add_employment_type", "يمكن إضافة نوع توظيف"),
            ("can_update_employment_type", "يمكن تحديث نوع توظيف"),
            ("can_delete_employment_type", "يمكن حذف نوع توظيف"),
    ]
        
    def save(self, *args, **kwargs):

        if self.is_default:
        # تحقق من وجود سجل آخر بقيمة is_default = True
            if EmployementType.objects.filter(is_default=True).exclude(pk=self.pk).exists():
                raise ValueError(_("لا يمكن أن يكون هناك أكثر من سجل واحد يحمل القيمة الافتراضية."))
            
        if self.pdf_file and not self.pdf_file.name.endswith('.pdf'):
            raise ValidationError(_("يجب أن يكون الملف من نوع PDF."))

            
        if not self.slug and self.name:
            self.slug = slugify(unidecode(self.name))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while EmployementType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(EmployementType, self).save(*args, **kwargs)  

    

    def __str__(self):
        return self.name


def employment_history_pdf_path(instance, filename):
    employee_name = instance.basic_info.get_full_name() if instance.basic_info else "unknown"
    start_date = instance.start_date.strftime("%Y-%m-%d") if instance.start_date else "start_unknown"
    end_date = instance.end_date.strftime("%Y-%m-%d") if instance.end_date else "end_unknown"
    return f"employment_history_pdfs/{employee_name}/{start_date}_to_{end_date}/{filename}"


class EmploymentHistory(models.Model):
    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employment_histories',
        verbose_name=_("الموظف")
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ البدء"),
        help_text=_("تاريخ بدء هذا السجل الوظيفي.")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء"),
        help_text=_("تاريخ انتهاء هذا السجل الوظيفي (إذا كان منتهيًا).")
        )
    
    employee_duration_day = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="مدة الخدمة - بالأيام",
        help_text= " يرجى ادخال مدة الخدمة بالايام في حال عدم توفر تاريخ البداية والنهاية"
    )
    employee_duration_month = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="مدة الخدمة - بالأشهر",
         help_text=  " يرجى ادخال مدة الخدمة بالاشهر في حال عدم توفر تاريخ البداية والنهاية"
    )
    employee_duration_year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=" مدة الخدمة - بالسنوات", 
        help_text=  " يرجى ادخال مدة الخدمة بالنوات في حال عدم توفر تاريخ البداية والنهاية"
        )

    
    employee_type = models.ForeignKey(
        EmployementType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='employment_type',
        verbose_name=_("نوع الوظيفية")
    )

    
    employee_place = models.ForeignKey(
        PlaceOfEmployment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='employment_place',
        verbose_name=_("مكان العمل")
    )

    pdf_file = models.FileField(
        upload_to=employment_history_pdf_path,
        blank=True,
        null=True,
        verbose_name="ملف PDF",
        help_text="ملف PDF متعلق بتاريخ التوظيف"
    )
    calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الحساب",
        help_text="تاريخ حساب مدة الخدمة"
    )
    comments = models.CharField(max_length=255,
                                  blank=True, null=True,
                                   help_text=_(" ملاحظات."))  # اسم الإجازة


    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_employment_history',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على ادخال البيانات.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug")
    class Meta:
        verbose_name = _("الخدمة الوظيفية ")
        verbose_name_plural = _("الخدمات الوظيفية ")
        permissions = [
                ("can_add_employment_history", "يمكن إضافة خدمة وظيفية للموظف "),
                ("can_update_employment_history", "يمكن تحديث الخدمة الوظيفية للموظف "),
                ("can_delete_employment_history", "يمكن حذف الخدمة الوظيفية للموظف "),
        ]
    

    def save(self, *args, **kwargs):
        if not self.employee_type:
            default_type = EmployementType.objects.filter(is_default=True).first()
            if default_type:
                self.employee_type = default_type  # تعيين نوع التوظيف الافتراضي
                
        if not self.employee_place:
            default_place = PlaceOfEmployment.objects.filter(is_default=True).first()
            if default_place:
                self.employee_place = default_place  # تعيين المكان الافتراضي

        if not self.slug:
            if self.basic_info:
                base_slug = slugify(unidecode (f"{self.basic_info.firstname}-{self.basic_info.thirdname}"))
            else:
                base_slug = slugify("unknown-h-title")
            slug = base_slug
            counter = 1
            while EmploymentHistory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
       
        if self.start_date or self.end_date:
            if not self.start_date:
                self.start_date = datetime.now().date()
            
            if not self.end_date:
                self.end_date = datetime.now().date()
            
            # الحساب التلقائي بناءً على start_date و end_date
            end_date = self.end_date if self.end_date else datetime.now().date()
            delta = relativedelta(end_date, self.start_date)

            # تحديث المدة بناءً على الحساب
            self.employee_duration_year = delta.years
            self.employee_duration_month = delta.months
            self.employee_duration_day = delta.days
        
        # إذا كانت المدة مذكورة يدويًا، نقوم باستخدامها كما هي
        self.employee_duration_year = self.employee_duration_year or 0
        self.employee_duration_month = self.employee_duration_month or 0
        self.employee_duration_day = self.employee_duration_day or 0

        if not self.calculated_at:
            if self.start_date:
                self.calculated_at = self.start_date
            else:
                self.calculated_at = datetime.now().date()


        super().save(*args, **kwargs)
    def __str__(self):

        employee_name = self.basic_info.get_full_name() if self.basic_info else "غير معروف"
        start_date = self.start_date.strftime("%Y-%m-%d") if self.start_date else "غير متوفر"
        end_date = self.end_date.strftime("%Y-%m-%d") if self.end_date else "حتى الآن"
        
        return f"{employee_name} | {start_date} - {end_date} | مدة الخدمة: {self.employee_duration_year} سنوات، {self.employee_duration_month} أشهر، {self.employee_duration_day} أيام - {self.calculated_at}"
    




######################### Log #########################

# نموذج سجل تغييرات نوع التوظيف
class EmployementTypeChangeLog(models.Model):
    employement_type = models.ForeignKey(
        EmployementType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع التوظيف")
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
        verbose_name = _("سجل تغييرات نوع التوظيف")
        verbose_name_plural = _("سجلات تغييرات أنواع التوظيف")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employement_type} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات تاريخ التوظيف
class EmploymentHistoryChangeLog(models.Model):
    employment_history = models.ForeignKey(
        EmploymentHistory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("سجل تاريخ التوظيف")
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
        verbose_name = _("سجل تغييرات تاريخ التوظيف")
        verbose_name_plural = _("سجلات تغييرات تاريخ التوظيف")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employment_history} - {self.action} - {self.timestamp}"


##################### Signals ############################


# الإشارات (Signals) الخاصة بـ EmployementType
@receiver(pre_save, sender=EmployementType)
def log_employement_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployementType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployementTypeChangeLog.objects.create(
                employement_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmployementType)
def log_employement_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployementTypeChangeLog.objects.create(
            employement_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmployementType)
def log_employement_type_deletion(sender, instance, **kwargs):
    EmployementTypeChangeLog.objects.create(
        employement_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



# الإشارات (Signals) الخاصة بـ EmploymentHistory
@receiver(pre_save, sender=EmploymentHistory)
def log_employment_history_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmploymentHistory.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmploymentHistoryChangeLog.objects.create(
                employment_history=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmploymentHistory)
def log_employment_history_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmploymentHistoryChangeLog.objects.create(
            employment_history=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmploymentHistory)
def log_employment_history_deletion(sender, instance, **kwargs):
    EmploymentHistoryChangeLog.objects.create(
        employment_history=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )