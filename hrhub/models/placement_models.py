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
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from collections import defaultdict
from .hr_utilities_models import PlaceOfEmployment, DutyAssignmentOrder


def placement_pdf_path(instance, filename):
    employee_name = f"{instance.basic_info.firstname}_{instance.basic_info.secondname}" if instance.basic_info else "unknown_employee"
    
    placement_type = instance.placement_type if instance.placement_type else "unknown_type"
    
    place_name = instance.place_of_placement.name_in_arabic if instance.place_of_placement and instance.place_of_placement.name_in_arabic else "unknown_place"
    
    # بناء المسار
    return f"placements/{placement_type}/{place_name}/{employee_name}/{filename}"

class Placement(models.Model):
    # خيارات التنسيب
    INTERNAL = 'internal'
    EXTERNAL = 'external'
    PLACEMENT_CHOICES = [
        (INTERNAL, 'تنسبيب الى الوزارة'),
        (EXTERNAL, 'تنسبيب خارج الوزارة'),
    ]
    
    # البيانات الخاصة بالتنسيب
    basic_info = models.ForeignKey(BasicInfo, on_delete=models.CASCADE, related_name="employee_placement")
    placement_type = models.CharField(
        max_length=8,
        choices=PLACEMENT_CHOICES,
        default=INTERNAL
    )
    place_of_placement = models.ForeignKey(PlaceOfEmployment, on_delete=models.SET_NULL, 
                                           null=True, blank=True, related_name='place_of_placement', 
                                           verbose_name="مكان التنسيب ", help_text=" مكان التنسيب اختياري   ")
    order_of_placement = models.ForeignKey(DutyAssignmentOrder, on_delete=models.SET_NULL, null=True, blank=True, 
                                           related_name='order_of_placement', 
                                           verbose_name="نوع امر التنسيب ", help_text=" يرجى اختيار نوع امر التنسيب - اختياري    ")
    name = models.CharField(max_length=255, 
                            blank=False, null=False,
                             verbose_name="رقم الامر الصادر", 
                             help_text="ادخل  رقم الامر  الصادر  بالتنسيب اختياري") 
    pdf_file = models.FileField(
        upload_to=placement_pdf_path,
        null=True,
        blank=True,
        verbose_name=" كتاب التنسيب",
        help_text="    يرجى ادخال الكتاب الصادر للتنسيب  "
    )


    start_date = models.DateField(null=False, blank=False, 
                                  verbose_name="تاريخ بداية التنسيب", help_text="تاريخ بداية التنسيب")

    end_date = models.DateField(null=True, blank=True,  
                                verbose_name="تاريخ نهاية التنسيب", help_text="تاريخ نهاية التنسيب")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_placement', verbose_name="أنشئ بواسطة", help_text="الموظف الذي قام بإنشاء الطلب")
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name="Slug")

    class Meta:
        verbose_name = "تنسيب الموظف "
        verbose_name_plural = "تنسيبات الموظفين "
        permissions = [
            ("can_add_placement", "يمكن إضافة تنسيب"),
            ("can_update_placement", "يمكن تحديث تنسيب"),
            ("can_delete_placement", "يمكن حذف تنسيب"),
            ("can_view_placement", "يمكن عرض تنسيب"),
        ]

    def get_description(self):
        return _("يهتم هذا الجدول بالتنسيب سواء كان داخلي او خارجي     ")
    
    def save(self, *args, **kwargs):
        if not self.slug and self.basic_info:
        # التأكد من الحقول
            employee_name = self.basic_info.firstname if self.basic_info.firstname else "unknown"
            place_title = self.place_of_placement.name_in_arabic[:2] if self.place_of_placement and self.place_of_placement.name_in_arabic else "NA"
        
        # إنشاء base_slug باستخدام بيانات مختصرة
            base_slug = f"{self.basic_info.secondname}-{employee_name[:4]}-{place_title}"
            base_slug = slugify(unidecode(base_slug))

        # التأكد من تفرد slug
            original_slug = base_slug
            counter = 1
            while Placement.objects.filter(slug=base_slug).exists():
                base_slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = base_slug

    # التحقق من سلامة التواريخ
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("تاريخ نهاية التنسيب لا يمكن أن يكون قبل تاريخ البداية.")
    
        super(Placement, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.basic_info.firstname} - {self.placement_type} "
    



class PlacementActivityLog(models.Model):
    placement = models.ForeignKey(
        Placement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
        verbose_name="التنسيب"
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
        Employee,  # المستخدم المسؤول
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم المسؤول"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التغيير")

    class Meta:
        verbose_name = "سجل حركة التنسيب"
        verbose_name_plural = "سجلات حركة التنسيب"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.placement} - {self.action} - {self.timestamp}"



from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=Placement)
def log_placement_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Placement.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            PlacementActivityLog.objects.create(
                placement=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=Placement)
def log_placement_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        PlacementActivityLog.objects.create(
            placement=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=Placement)
def log_placement_deletion(sender, instance, **kwargs):
    PlacementActivityLog.objects.create(
        placement=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )
