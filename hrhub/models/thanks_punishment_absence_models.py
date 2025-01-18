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
from collections import defaultdict
from .hr_utilities_models import PlaceOfEmployment
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن
from django.db.models.signals import pre_save, post_save, post_delete




class ThanksType(models.Model):
    
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_thanks_type',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على ادخال البيانات.")
    )
    thanks_name = models.CharField(
        max_length=255,
        verbose_name=_("اسم الشكر"),
        help_text=_("اسم نوع الشكر")
    )
    thanks_impact = models.PositiveIntegerField(
        default=0, 
        null=True,
        blank=True,
        verbose_name=_("تأثير الشكر"),
        help_text=_("تأثير هذا النوع من كتب الشكر على  الاستحقاقات الادارية بالاشهر (عدد صحيح موجب)")
    )
    comments = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("ملاحظات "),
        help_text=_("ملاحظات إضافية عن هذا النوع من الشكر - اختياري-")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("تاريخ و وقت انشاء نوع الشكر")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث"),
        help_text=_(" تاريخ ووقت   آخر تحديث لهذا النوع من الشكر")
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name=_("المعرف"),
        help_text=_("نسخة ملائمة للرابط لاسم نوع الشكر")
    )

    class Meta:
        verbose_name = "نوع كتاب الشكر للموظف "
        verbose_name_plural = "انواع كتب الشكر للموظفين "
        permissions = [
            ("can_add_thanks_type", "يمكن إضافة نوع كتاب شكر"),
            ("can_update_thanks_type", "يمكن تحديث نوع كتاب شكر"),
            ("can_delete_thanks_type", "يمكن حذف نوع كتاب شكر"),
    ]
    
    def save(self, *args, **kwargs):
        if self.thanks_impact is None:
            self.thanks_impact = 0
            
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug:
            self.slug = slugify(unidecode(self.thanks_name))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while ThanksType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(ThanksType, self).save(*args, **kwargs)
    def get_description(self):
        return _("يهتم هذا الجداول  مع انواع كتب الشكر و التقدير من حيث اضافة اسم نوع او تحديثه او حذف ")

    def __str__(self):
        return f"{self.created_by} - {self.thanks_name} - {self.thanks_impact}"

def employee_thanks_pdf_path(instance, filename):
    employee_names = instance.emp_id_thanks.all().values_list('firstname', 'secondname', 'thirdname')
    employee_names_str = '-'.join([f"{first}_{second}_{last}" for first, second, last in employee_names])
    thanks_type_name = instance.thanks_type.thanks_name if instance.thanks_type else "unknown_thanks_type"
    thanks_number = instance.thanks_number if instance.thanks_number else "unknown_thanks_number"
    return f"employee_thanks_pdfs/{thanks_type_name}/{thanks_number}/{employee_names_str}/{filename}"


class EmployeeThanks(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الموظف",
        help_text="الموظف الذي أدخل نوع الشكر هذا"
    )
    emp_id_thanks = models.ManyToManyField(
        BasicInfo,
        verbose_name="الموظف المستحق لكتاب الشكر ",
        help_text="الموظف (أو الموظفون) الذين تم يستحقون كتاب الشكر",
        related_name='thanks_letters'
    )
    thanks_type = models.ForeignKey(
        ThanksType,
        on_delete=models.CASCADE,
        verbose_name="نوع الشكر",
        help_text="نوع الشكر",
        related_name='thanks_type'
    )
    pdf_file = models.FileField(
        upload_to=employee_thanks_pdf_path,
        blank=True,
        null=True,
        verbose_name="نسخة pdf من كتاب الشكر ",
        help_text="   يرجى رفع ملف كتاب الشكر والتقدير بصيغة pdf"
    )
    thanks_number = models.CharField(
        max_length=255,
        verbose_name="رقم كتاب الشكر ",
        help_text="أدخل رقم كتاب الشكر ."
    )
    date_issued = models.DateField(
        verbose_name="تاريخ اصدار كتاب الشكر",
        help_text="أدخل تاريخ إصدار كتاب الشكر."
    )
    COUNT_CHOICES = [
        (True, "يتم احتسابه"),
        (False, "لا يتم احتسابه"),
    ]
    APPROVAL_CHOICES = [
        (True, "موافق عليه"),
        (False, "غير موافق عليه"),
    ]

    is_counted = models.BooleanField(
        default=True,
        choices=COUNT_CHOICES,
        verbose_name="يتم احتسابه",
        help_text="يشير إذا كان هذا الشكر يُحسب ضمن الثلاثة المسموح بها."
    )

    approved = models.BooleanField(
        default=True,
        choices=APPROVAL_CHOICES,
        verbose_name="موافق عليه",
        help_text="يحدد ما إذا كانت العلاقة قد تمت الموافقة عليها."
    )
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name="ملاحظات",
        help_text="ملاحظات إضافية توضح سبب الحالة."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
        help_text="الطابع الزمني عند إنشاء الشكر"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ التحديث",
        help_text="الطابع الزمني عند آخر تحديث للشكر"
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="المعرف الفريد",
        help_text="نسخة ملائمة للرابط لاسم الشكر"
    )

    class Meta:
        verbose_name = "كتاب الشكر للموظف"
        verbose_name_plural = "كتب الشكر للموظفين"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['thanks_type']),
        ]
        permissions = [
            ("can_add_employee_thanks", "يمكن إضافة كتاب شكر"),
            ("can_update_employee_thanks", "يمكن تحديث كتاب شكر"),
            ("can_delete_employee_thanks", "يمكن حذف كتاب شكر"),
            ("can_view_employee_thanks", "يمكن عرض كتب الشكر"),
    ]
    def save(self, *args, **kwargs):
    

        # إنشاء slug فريد
        if not self.slug:
            slug_base = f"{self.thanks_type.thanks_name} - {self.thanks_number}"
            unique_slug = slugify(unidecode(slug_base))

            # التحقق من وجود slug مشابه والتعديل إذا لزم الأمر
            count = 1
            while EmployeeThanks.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                count += 1

            self.slug = unique_slug


        super().save(*args, **kwargs)
    def get_description(self):
        return _("يهتم هذا الجداول  مع اعطاء كتب الشكر و التقدير للموظفين المستحقين من حيث اضافة موظف  او تحديثه او حذف ")
    
    
    @staticmethod
    def count_thanks_per_employee():
        # حساب عدد كتب الشكر لكل موظف
        from collections import defaultdict
        
        # إنشاء قاموس لتخزين عدد الكتب لكل موظف
        employee_thanks_count = defaultdict(int)
        
        # الحصول على جميع السجلات من EmployeeThanks
        employee_thanks = EmployeeThanks.objects.all()
        
        # تكرار عبر السجلات وعدّ كل موظف مرتبط بكتاب الشكر
        for thanks in employee_thanks:
            for employee in thanks.emp_id_thanks.all():
                employee_thanks_count[employee] += 1
        
        # إرجاع القاموس الذي يحتوي على عدد الكتب لكل موظف
        return employee_thanks_count
    
    @staticmethod
    def count_counted_thanks_per_employee():
    # حساب عدد كتب الشكر المعتبرة لكل موظف (التي يتم احتسابها)
        from collections import defaultdict
    
    # إنشاء قاموس لتخزين عدد الكتب المعتبرة لكل موظف
        employee_thanks_count = defaultdict(int)
        employee_thanks_impact = defaultdict(int)
    
    # الحصول على جميع السجلات من EmployeeThanks والتي يتم احتسابها (is_counted=True)
        employee_thanks = EmployeeThanks.objects.filter(is_counted=True)
    
    # تكرار عبر السجلات وعدّ كل موظف مرتبط بكتاب الشكر
        for thanks in employee_thanks:
            for employee in thanks.emp_id_thanks.all():
                impact = thanks.thanks_type.thanks_impact  # تأثير نوع الشكر
                employee_thanks_impact[employee] += impact
                employee_thanks_count[employee] += 1
    
    # إرجاع القاموس الذي يحتوي على عدد الكتب المعتبرة لكل موظف
        return employee_thanks_impact
    
    def __str__(self):
        # استخراج أسماء الموظفين المستحقين
        employee_names = self.emp_id_thanks.all().values_list('firstname', 'secondname', 'surname')
        # دمج الأجزاء المختلفة للاسم
        employee_names_str = ', '.join([f"{first} {second} {last}" for first, second, last in employee_names])

        # حساب عدد كتب الشكر لكل موظف
        thanks_count = self.count_thanks_per_employee()
        thanks_impact_count = self.count_counted_thanks_per_employee()
        
        # دمج عدد الكتب مع النص المطبوع
        employee_names_str_with_count = ', '.join([f"{name} ({thanks_count[employee]})" for employee, name in zip(self.emp_id_thanks.all(), employee_names)])
        employee_names_str_with__true_count = ', '.join([f"{name} ({thanks_impact_count.get(employee, 0)})" 
                                                for employee, name in zip(self.emp_id_thanks.all(), employee_names)])
        return f"شكر لـ {employee_names_str_with_count} - {employee_names_str_with__true_count} - {self.thanks_type.thanks_name} ({self.thanks_number})"



class PunishmentType(models.Model):
    created_by = models.ForeignKey(
        Employee,  # استخدام مرجع نصي
        on_delete=models.CASCADE,
        verbose_name="الموظف",
        help_text="الموظف الذي أدخل نوع العقوبة هذا"
    )
    punishment_name = models.CharField(
        max_length=255,
        verbose_name="اسم العقوبة",
        help_text="اسم نوع العقوبة"
    )
    punishment_impact = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name="تأثير العقوبة",
        help_text="تأثير العقوبة (عدد صحيح إيجابي)"
    )
    comments = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ملاحظات ان وجدت ",
        help_text="ملاحظات عامة عن هذا النوع من العقوبة"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
        help_text="الطابع الزمني عند إنشاء نوع العقوبة"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ التحديث",
        help_text="الطابع الزمني عند آخر تحديث لنوع العقوبة"
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="الـSlug",
        help_text="نسخة ملائمة للرابط لاسم نوع العقوبة"
    )

    class Meta:
        verbose_name = "نوع العقوبة"
        verbose_name_plural = "أنواع العقوبات"
        permissions = [
            ("can_add_punishment_type", "يمكن إضافة نوع عقوبة"),
            ("can_update_punishment_type", "يمكن تحديث نوع عقوبة"),
            ("can_delete_punishment_type", "يمكن حذف نوع عقوبة"),
            ("can_view_punishment_type", "يمكن عرض نوع عقوبة"),
        ]


    def save(self, *args, **kwargs):
        if not self.punishment_impact:
            self.punishment_impact = 0
        if not self.slug:
            # تجهيز النص الأساسي لتوليد الـ slug
            slug_base = f"{self.created_by} {self.punishment_name} {self.punishment_impact}"
            
            # تحويل النص باستخدام unidecode قبل تمريره إلى slugify
            slug = slugify(unidecode(slug_base))
            
            # التحقق من كونه فريدًا عبر حل التكرارات
            unique_slug = slug
            count = 1
            while PunishmentType.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slug}-{count}"
                count += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.created_by} - {self.punishment_name} - {self.punishment_impact}"
    
    def get_description(self):
        return _("يهتم هذا الجداول  مع اسماء انواع كتب العقوبة من حيث الاضافة  او التحديث او الحذف ")


def employee_punishment_pdf_path(instance, filename):
    employee_names = instance.emp_id_punishment.all().values_list('firstname', 'secondname', 'thirdname')
    employee_names_str = '-'.join([f"{first}_{second}_{last}" for first, second, last in employee_names])

    punishment_type_name = instance.punishment_type.punishment_name if instance.punishment_type else "unknown_punishment_type"
    punishment_number = instance.punishment_number if instance.punishment_number else "unknown_punishment_number"

    return f"employee_punishment_pdfs/{punishment_type_name}/{punishment_number}/{employee_names_str}/{filename}"



class EmployeePunishment(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الموظف",
        help_text="الموظف الذي أدخل نوع العقوبة هذا"
    )
    emp_id_punishment = models.ManyToManyField(
        BasicInfo,
        verbose_name="موظف العقوبة",
        help_text="الموظف (أو الموظفون) الذين تم معاقبتهم",
        related_name='employee_punishment_recipients'
    )
    punishment_type = models.ForeignKey(
        PunishmentType,
        on_delete=models.CASCADE,
        verbose_name="نوع العقوبة",
        help_text="نوع العقوبة",
        related_name='punishment_type'
    )
    pdf_file = models.FileField(
        upload_to=employee_punishment_pdf_path,
        blank=True,
        null=True,
        verbose_name=" كتاب العقوبة",
        help_text="  يرجى ادخال كتاب العقوبة -اختياري- "
    )
    punishment_number = models.CharField(
        max_length=255,
        verbose_name="رقم كتاب العقوبة",
        help_text="أدخل رقم كتاب العقوبة."
    )
    date_issued = models.DateField(
        verbose_name="تاريخ إصدار كتاب العقوبة",
        help_text="أدخل تاريخ إصدار كتاب العقوبة."
    )
    COUNT_CHOICES = [
        (True, "يتم احتسابه"),
        (False, "لا يتم احتسابه"),
    ]
    APPROVAL_CHOICES = [
        (True, "موافق عليه"),
        (False, "غير موافق عليه"),
    ]

    is_counted = models.BooleanField(
        default=False,
        choices=COUNT_CHOICES,
        verbose_name="يتم احتسابه",
        help_text="يشير إذا كان هذا الشكر يُحسب ضمن الثلاثة المسموح بها."
    )
    approved = models.BooleanField(
        default=True,
        choices=APPROVAL_CHOICES,
        verbose_name="موافق عليه",
        help_text="يحدد ما إذا كانت العلاقة قد تمت الموافقة عليها."
    )
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name="ملاحظات",
        help_text="ملاحظات إضافية توضح سبب الحالة."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
        help_text="الطابع الزمني عند إنشاء العقوبة"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ التحديث",
        help_text="الطابع الزمني عند آخر تحديث للعقوبة"
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="المعرف الفريد",
        help_text="نسخة ملائمة للرابط لاسم العقوبة"
    )

    class Meta:
        verbose_name = "كتاب العقوبة للموظف"
        verbose_name_plural = "كتب العقوبات للموظفين"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['punishment_type']),
        ]
        permissions = [
            ("can_add_employee_punishment", "يمكن إضافة كتاب عقوبة"),
            ("can_update_employee_punishment", "يمكن تحديث كتاب عقوبة"),
            ("can_delete_employee_punishment", "يمكن حذف كتاب عقوبة"),
            ("can_view_employee_punishment", "يمكن عرض كتاب عقوبة"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = f"{self.punishment_type.punishment_name} - {self.punishment_number}"
            unique_slug = slugify(unidecode(slug_base))
            
            count = 1
            while EmployeePunishment.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                count += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)
    
    def get_description(self):
        return _("يهتم هذا الجداول  مع اعطاء كتب العقوبة الى الموظفين الصادرة بحقهم عقوبة و تحديث البيانات وحذفها ")

    @staticmethod
    def count_punishments_per_employee():
        employee_punishments_count = defaultdict(int)
        employee_punishments = EmployeePunishment.objects.all()

        for punishment in employee_punishments:
            for employee in punishment.emp_id_punishment.all():
                employee_punishments_count[employee] += 1

        return employee_punishments_count

    @staticmethod
    def count_counted_punishments_per_employee():
        employee_punishments_impact = defaultdict(int)
        employee_punishments = EmployeePunishment.objects.filter(is_counted=True)

        for punishment in employee_punishments:
            for employee in punishment.emp_id_punishment.all():
                impact = punishment.punishment_type.punishment_impact
                employee_punishments_impact[employee] += impact

        return employee_punishments_impact

    def __str__(self):
        employee_names = self.emp_id_punishment.all().values_list('firstname', 'secondname', 'surname')
        employee_names_str = ', '.join([f"{first} {second} {last}" for first, second, last in employee_names])

        punishment_count = self.count_punishments_per_employee()
        punishment_impact = self.count_counted_punishments_per_employee()

        employee_names_with_count = ', '.join([
            f"{name} ({punishment_count[employee]})"
            for employee, name in zip(self.emp_id_punishment.all(), employee_names)
        ])

        employee_names_with_impact = ', '.join([
            f"{name} ({punishment_impact.get(employee, 0)})"
            for employee, name in zip(self.emp_id_punishment.all(), employee_names)
        ])

        return f"عقوبة لـ {employee_names_with_count} - {employee_names_with_impact} - {self.punishment_type.punishment_name} ({self.punishment_number})"




class AbsenceType(models.Model):
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_absence_type',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على نوع الغياب.")
    )
    absence_name = models.CharField(
        max_length=255,
        verbose_name=_("اسم الغياب"),
        help_text=_("اسم نوع الغياب")
    )
    absence_impact = models.PositiveIntegerField(
        default=0,
        verbose_name=_("تأثير الغياب"),
        help_text=_("تأثير الغياب (عدد صحيح موجب)")
    )
    comments = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("ملاحظات اضافية "),
        help_text=_("  اضافة ملاحظات اضافية عن هذا النوع من الغياب -اختياري ")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("الطابع الزمني عند إنشاء نوع الغياب")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث"),
        help_text=_("الطابع الزمني عند آخر تحديث لنوع الغياب")
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name=_("المعرف"),
        help_text=_("نسخة ملائمة للرابط لاسم نوع الغياب")
    )

    class Meta:
        verbose_name = "نوع غياب الموظف"
        verbose_name_plural = "أنواع غياب الموظفين"
        permissions = [
            ("can_add_absence_type", "يمكن إضافة نوع غياب"),
            ("can_update_absence_type", "يمكن تحديث نوع غياب"),
            ("can_delete_absence_type", "يمكن حذف نوع غياب"),
            ("can_view_absence_type", "يمكن عرض نوع غياب"),
        ]

    def save(self, *args, **kwargs):
        if not self.absence_impact:
            self.absence_impact = 0
        if not self.slug:
            self.slug = slugify(unidecode(self.absence_name))
            original_slug = self.slug
            counter = 1
            while AbsenceType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f" {self.absence_name} - {self.absence_impact}"
    
    def get_description(self):
        return _("يهتم هذا الجداول  مع اسماء انواغ الغياب من حيث الاضافة و تحديث البيانات وحذفها ")



def employee_absence_pdf_path(instance, filename):
    employee_names = instance.emp_id_absence.all().values_list('firstname', 'secondname', 'thirdname')
    employee_names_str = '-'.join([f"{first}_{second}_{last}" for first, second, last in employee_names])
    absence_type_name = instance.absence_type.absence_name if instance.absence_type else "unknown_absence_type"
    absence_number = instance.absence_number if instance.absence_number else "unknown_absence_number"
    return f"employee_absence_pdfs/{absence_type_name}/{absence_number}/{employee_names_str}/{filename}"

class EmployeeAbsence(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("الموظف"),
        help_text=_("الموظف الذي أدخل بيانات الغياب")
    )
    emp_id_absence = models.ManyToManyField(
            BasicInfo,
            verbose_name="الموظف الغائب ",
            help_text="الموظف (أو الموظفون) الذين الغائبون",
            related_name='employee_absence_recipients'
        )
    absence_type = models.ForeignKey(
        AbsenceType,
        on_delete=models.CASCADE,
        verbose_name=_("نوع الغياب"),
        help_text=_("نوع الغياب"),
        related_name='absence_type'
    )
    pdf_file = models.FileField(
        upload_to=employee_absence_pdf_path,
        blank=True,
        null=True,
        verbose_name=_("ملف PDF"),
        help_text=_("ملف PDF متعلق بالغياب")
    )
    absence_number = models.CharField(
        max_length=255,
        verbose_name=_("رقم كتاب الغياب"),
        help_text=_("أدخل رقم كتاب الغياب.")
    )
    date_issued = models.DateField(
        verbose_name=_("تاريخ صدور الامر"),
        help_text=_("أدخل تاريخ صدور امر الغياب."),
        
            )
    start_date = models.DateField(null=False, blank=False, verbose_name="تاريخ بداية الغياب", help_text="تاريخ بداية الغياب")
    end_date = models.DateField(null=False, blank=False, verbose_name="تاريخ نهاية الغياب", help_text="تاريخ نهاية الغياب")
    duration_years = models.IntegerField(null=True, blank=True, verbose_name="مدة الغياب بالسنوات",
                                          help_text="مدة الغياب بالسنوات -اختياري")
    duration_months = models.IntegerField(null=True, blank=True, verbose_name="مدة الغياب بالشهور",
                                           help_text="مدة الغياب بالشهور - اختياري")
    duration_days = models.IntegerField(null=True, blank=True, verbose_name="مدة الغياب بالأيام", 
                                        help_text="مدة الغياب بالايام - اختياري")

    approved = models.BooleanField(
        default=True,
       
        verbose_name=_("موافق عليه"),
        help_text=_("يحدد ما إذا كانت العلاقة قد تمت الموافقة عليها.")
    )
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات"),
        help_text=_("ملاحظات إضافية توضح سبب الحالة.")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("الطابع الزمني عند إنشاء سجل الغياب")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث"),
        help_text=_("الطابع الزمني عند آخر تحديث لسجل الغياب")
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name=_("المعرف الفريد"),
        help_text=_("نسخة ملائمة للرابط لسجل الغياب")
    )

    class Meta:
        verbose_name = "سجل غياب الموظف"
        verbose_name_plural = "سجلات غياب الموظفين"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['absence_type']),
        ]
        permissions = [
            ("can_add_employee_absence", _("يمكن إضافة سجل غياب")),
            ("can_update_employee_absence", _("يمكن تحديث سجل غياب")),
            ("can_delete_employee_absence", _("يمكن حذف سجل غياب")),
            ("can_view_employee_absence", _("يمكن عرض سجل غياب")),
        ]


    def save(self, *args, **kwargs):

        if not self.duration_years or not self.duration_months or not self.duration_days:
            if not self.end_date:
                self.end_date = date.today()

            if self.start_date and self.end_date:
                delta = relativedelta(self.end_date, self.start_date)
                self.duration_years = delta.years
                self.duration_months = delta.months
                self.duration_days = delta.days
                
        if not self.slug:
            slug_base = f"{self.absence_type.absence_name} - {self.absence_number}"
            unique_slug = slugify(unidecode(slug_base))
            count = 1
            while EmployeeAbsence.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slugify(unidecode(slug_base))}-{count}"
                count += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)
    
    def get_description(self):
        return _("يهتم هذا الجداول  مع الموظفين الغائبين والصادرة بحقهم قرارات غياب او حذفها او تحديث المعلومات  ")

############################ Log ###################
# نموذج سجل تغييرات نوع الشكر
class ThanksTypeChangeLog(models.Model):
    thanks_type = models.ForeignKey(
        ThanksType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع الشكر")
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
        verbose_name = _("سجل تغييرات نوع الشكر")
        verbose_name_plural = _("سجلات تغييرات أنواع الشكر")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.thanks_type} - {self.action} - {self.timestamp}"



class EmployeeThanksChangeLog(models.Model):
    employee_thanks = models.ForeignKey(
        EmployeeThanks,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("كتاب الشكر")
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
        verbose_name = _("سجل تغييرات كتب الشكر")
        verbose_name_plural = _("سجلات تغييرات كتب الشكر")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_thanks} - {self.action} - {self.timestamp}"

class PunishmentTypeChangeLog(models.Model):
    punishment_type = models.ForeignKey(
        PunishmentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name="نوع العقوبة"
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name="نوع العملية"
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="اسم الحقل"
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة القديمة"
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة الجديدة"
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم المسؤول"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التغيير")

    class Meta:
        verbose_name = "سجل تغييرات نوع العقوبة"
        verbose_name_plural = "سجلات تغييرات أنواع العقوبات"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.punishment_type} - {self.action} - {self.timestamp}"


class EmployeePunishmentChangeLog(models.Model):
    employee_punishment = models.ForeignKey(
        EmployeePunishment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name="كتاب العقوبة"
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name="نوع العملية"
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="اسم الحقل"
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة القديمة"
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة الجديدة"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم المسؤول"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التغيير")

    class Meta:
        verbose_name = "سجل تغييرات عقوبات الموظفين"
        verbose_name_plural = "سجلات تغييرات عقوبات الموظفين"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_punishment} - {self.action} - {self.timestamp}"
    
class AbsenceTypeChangeLog(models.Model):
    absence_type = models.ForeignKey(
        AbsenceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name="نوع الغياب"
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name="نوع العملية"
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="اسم الحقل"
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة القديمة"
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة الجديدة"
    )
    user = models.ForeignKey(
        Employee,  # أو النموذج المناسب للمستخدم
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم المسؤول"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التغيير")

    class Meta:
        verbose_name = "سجل تغييرات نوع الغياب"
        verbose_name_plural = "سجلات تغييرات أنواع الغياب"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.absence_type} - {self.action} - {self.timestamp}"


class EmployeeAbsenceChangeLog(models.Model):
    employee_absence = models.ForeignKey(
        EmployeeAbsence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name="سجل الغياب"
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name="نوع العملية"
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="اسم الحقل"
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة القديمة"
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="القيمة الجديدة"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم المسؤول"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التغيير")

    class Meta:
        verbose_name = "سجل تغييرات غياب الموظفين"
        verbose_name_plural = "سجلات تغييرات غياب الموظفين"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_absence} - {self.action} - {self.timestamp}"



############################## Signals  ############################
# إشارات (Signals) الخاصة بـ ThanksType
@receiver(pre_save, sender=ThanksType)
def log_thanks_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = ThanksType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            ThanksTypeChangeLog.objects.create(
                thanks_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=ThanksType)
def log_thanks_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        ThanksTypeChangeLog.objects.create(
            thanks_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=ThanksType)
def log_thanks_type_deletion(sender, instance, **kwargs):
    ThanksTypeChangeLog.objects.create(
        thanks_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )

    #### ####


@receiver(pre_save, sender=EmployeeThanks)
def log_employee_thanks_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeThanks.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeThanksChangeLog.objects.create(
                employee_thanks=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeThanks)
def log_employee_thanks_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeThanksChangeLog.objects.create(
            employee_thanks=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=EmployeeThanks)
def log_employee_thanks_deletion(sender, instance, **kwargs):
    EmployeeThanksChangeLog.objects.create(
        employee_thanks=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )




@receiver(pre_save, sender=PunishmentType)
def log_punishment_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = PunishmentType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            PunishmentTypeChangeLog.objects.create(
                punishment_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=PunishmentType)
def log_punishment_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        PunishmentTypeChangeLog.objects.create(
            punishment_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=PunishmentType)
def log_punishment_type_deletion(sender, instance, **kwargs):
    PunishmentTypeChangeLog.objects.create(
        punishment_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )




@receiver(pre_save, sender=EmployeePunishment)
def log_employee_punishment_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeePunishment.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeePunishmentChangeLog.objects.create(
                employee_punishment=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeePunishment)
def log_employee_punishment_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeePunishmentChangeLog.objects.create(
            employee_punishment=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=EmployeePunishment)
def log_employee_punishment_deletion(sender, instance, **kwargs):
    EmployeePunishmentChangeLog.objects.create(
        employee_punishment=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )




@receiver(pre_save, sender=AbsenceType)
def log_absence_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = AbsenceType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            AbsenceTypeChangeLog.objects.create(
                absence_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=AbsenceType)
def log_absence_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        AbsenceTypeChangeLog.objects.create(
            absence_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=AbsenceType)
def log_absence_type_deletion(sender, instance, **kwargs):
    AbsenceTypeChangeLog.objects.create(
        absence_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



@receiver(pre_save, sender=EmployeeAbsence)
def log_employee_absence_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeAbsence.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeAbsenceChangeLog.objects.create(
                employee_absence=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeAbsence)
def log_employee_absence_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeAbsenceChangeLog.objects.create(
            employee_absence=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=EmployeeAbsence)
def log_employee_absence_deletion(sender, instance, **kwargs):
    EmployeeAbsenceChangeLog.objects.create(
        employee_absence=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )
