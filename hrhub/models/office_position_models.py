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
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from collections import defaultdict
from .hr_utilities_models import DutyAssignmentOrder


class Office(MPTTModel):
    name = models.CharField(
        max_length=255,
         verbose_name=_("اسم الوحدة الادارية"),
        help_text=_("اسم الوحدة الادراية.")
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("الوحدة الادارية الاعلى"),
        help_text=_("الوحدة الادارية الاعلى . يمكن أن يكون خالياً.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text=_("نسخة ملائمة للرابط لاسم الوحدة الادارية.")
    )
    created_by = models.ForeignKey(
    Employee,
    null=True,  # يمكن أن يكون فارغًا
    blank=True, # يمكن أن يكون فارغًا في النماذج
    on_delete=models.CASCADE,
    verbose_name=_("الموظف الذي قام بالإنشاء"),
    help_text=_("الموظف الذي أدخل هذه الدائرة")
)
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات"),
        help_text=_("إضافة ملاحظات إضافية  (اختياري).")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("وقت إنشاء الدائرة.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("وقت آخر تحديث للمكتب.")
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        ordering = ['created_at']
        verbose_name = "الوحدة الادارية"
        verbose_name_plural = "الوحدات الادارية"
        permissions = [
            ("can_add_office", "يمكن إضافة وحدة إدارية"),
            ("can_update_office", "يمكن تحديث وحدة إدارية"),
            ("can_delete_office", "يمكن حذف وحدة إدارية"),
    ]

    def get_description(self):
        return f"يهتم هذا الجدول بالوحدات الادارية من دوائر ومديريات واقسام وشعب ووحدات وغيرها"

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(unidecode(self.name))
            original_slug = self.slug
            counter = 1
            while Office.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super(Office, self).save(*args, **kwargs)

    def __str__(self):
        """
        التمثيل النصي للوظيفة.
        """
        return f"{self.name}"
    


class EmployeeOffice(models.Model):
    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employee_offices',
        verbose_name=_("الموظف"),
        help_text=_("الموظف المرتبط بهذه الدائرة.")
    )
    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        related_name='employee_offices',
        verbose_name=_("الدائرة"),
        help_text=_("الدائرة التي يعمل بها الموظف.")
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانضمام"),
        help_text=_("تاريخ انضمام الموظف للدائرة.")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء"),
        help_text=_("تاريخ انتهاء العلاقة بالدائرة (اختياري).")
    )
   
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات"),
        help_text=_("إضافة ملاحظات إضافية حول العلاقة (اختياري).")
    )
    created_by = models.ForeignKey(
    Employee,
    null=True,  # يمكن أن يكون فارغًا
    blank=True, # يمكن أن يكون فارغًا في النماذج
    on_delete=models.CASCADE,
    verbose_name=_("الموظف الذي قام بادخال البيانات"),
    help_text=_("الموظف الذي أدخل هذا البيانات")
)
    slug = models.SlugField(
    max_length=255,
    unique=True,
    null=True,
    blank=True,
    verbose_name=_("Slug"),
    help_text=_("حقل slug يتم توليده تلقائيًا من اسم الموظف.")
)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("آخر تحديث")
    )

    class Meta:
       
        verbose_name = _("علاقة موظف بدائرة")
        verbose_name_plural = _("علاقات موظفين بدوائر")
        ordering = ['office', 'start_date']
        permissions = [
            ("can_add_employee_office", "يمكن إضافة موظف الى دائرة "),
            ("can_update_employee_office", "يمكن تحديث دائرة الموظف "),
            ("can_delete_employee_office", "يمكن حذف دائرة  الموظف"),
            ]
    
    def save(self, *args, **kwargs):
       
        if not self.slug and self.basic_info:
            self.slug = slugify(unidecode(self.basic_info.thirdname))
            original_slug = self.slug
            counter = 1
            while EmployeeOffice.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.basic_info} في {self.office}"
    
    def get_description(self):
        return f"يهتم هذا الجدول بترتيب الموظفين في دوائرة  "



class Position(MPTTModel):
    name = models.CharField(
        max_length=255,
        help_text=_("اسم الوظيفة.")
    )
    office = models.ForeignKey(
        Office,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='positions',
        help_text=_("مكتب الوظيفة.")
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text=_("الوظيفة الأب. يمكن أن تكون خالية.")
    )
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات"),
        help_text=_("إضافة ملاحظات إضافية   (اختياري).")
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text=_("نسخة ملائمة للرابط لاسم الوظيفة.")
    )
    created_by = models.ForeignKey(
    Employee,
    null=True,  # يمكن أن يكون فارغًا
    blank=True, # يمكن أن يكون فارغًا في النماذج
    on_delete=models.CASCADE,
    verbose_name=_("الموظف الذي قام بالإنشاء"),
    help_text=_("الموظف الذي أدخل هذا المنصب")
)

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("الطابع الزمني عند إنشاء الوظيفة.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("الطابع الزمني عند آخر تحديث للوظيفة.")
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("المنصب الوظيفي")
        verbose_name_plural = _("المناصب الوظيفي")
        ordering = ['office', 'name']  # ترتيب حسب المكتب ثم الاسم
        permissions = [
            ("can_add_position", "يمكن إضافة منصب وظيفي"),
            ("can_update_position", "يمكن تحديث منصب وظيفي"),
            ("can_delete_position", "يمكن حذف منصب وظيفي"),
    ]

    def save(self, *args, **kwargs):
       
        if not self.slug and self.name:
            self.slug = slugify(unidecode(self.name))
            original_slug = self.slug
            counter = 1
            while Position.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        """
        التمثيل النصي للوظيفة.
        """
        return f"{self.name}"
    
    def get_description(self):
        return f"يهتم هذا الجدول باسماء المناصب الادارية في الوزارة "
    

def user_employeeofficeposition_path(instance, filename):
    
    employee_name = instance.basic_info.firstname
    return f"employee_documents/employees/{employee_name}/documents/{filename}"


class EmployeeOfficePosition(models.Model):
    """
    نموذج يمثل علاقة الموظف بالمكتب والوظيفة.
    """

    basic_info = models.ForeignKey(
        BasicInfo,  # قم بتغيير BasicInfo إلى اسم نموذج الموظف المناسب
        on_delete=models.CASCADE,
        related_name='employee_office_positions',
        verbose_name=_("الموظف"),
        help_text=_("الموظف المرتبط بهذه العلاقة.")
    )
    office = models.ForeignKey(
        Office,  # قم بتغيير Office إلى اسم نموذج المكتب المناسب
        on_delete=models.CASCADE,
        null=True,  # يمكن أن يكون فارغًا
    blank=True,
        related_name='employee_positions',
        verbose_name=_("المكتب"),
        help_text=_("المكتب الذي يعمل فيه الموظف.")
    )
    position = models.ForeignKey(
        Position,  #   Position  اسم نموذج الوظيفة المناسب
        on_delete=models.CASCADE,
        null=True,  # يمكن أن يكون فارغًا
    blank=True,
        related_name='employee_positions',
        verbose_name=_("الوظيفة"),
        help_text=_("الوظيفة التي يشغلها الموظف في المكتب.")
    )
    duty_assignment_order = models.ForeignKey(
        DutyAssignmentOrder,  
        on_delete=models.CASCADE,
        null=True,  # يمكن أن يكون فارغًا
    blank=True,
        related_name='employee_duty_assignment_order',
        verbose_name=_("نوع الأمر الصادر"),
        help_text=_("نوع الأمر الصادر بحق هذا الموظف.")
    )
    duty_assignment_order_number = models.CharField(
        max_length=50,

        null=True,
        blank=True,
        verbose_name=_("رقم الامر الصادر"),
        help_text=_("إضافة رقم الامر الصادر بالموظف (اختياري).")
    )
    duty_assignment_order_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الامر الصادر"),
        help_text=_("تاريخ الامر الصادر.")
    )
    is_primary = models.BooleanField(
        default=False,
        
        verbose_name=_("اصالة "),
        help_text=_("يحدد ما إذا التكليف اصالة ام وكالة.")
    )
    start_date = models.DateField(
        null=True,  # يمكن أن يكون فارغًا
    blank=True,
        verbose_name=_("تاريخ المباشرة بالمنصب"),
        help_text=_("تاريخ المباشرة بالمنصب والمكتب .")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الانتهاء"),
        help_text=_("تاريخ انتهاء العمل في المكتب والوظيفة (يمكن أن يكون خالياً).")
    )
    user_employeeofficeposition = models.ImageField(
        upload_to='user_employeeofficeposition_path/',  # قم بتغيير المسار إذا لزم الأمر
        null=True,
        blank=True,
        verbose_name=_("الوثيقة"),
        help_text=_("وثيقة الأمر الصادر بحق الموظف.")
    )
    STATUS_CHOICES = [
        ('ongoing', 'مستمر'),
        ('ended', 'منتهي'),
    ]

    status = models.CharField(
        max_length=10,  # تأكد أن الطول يكفي لتخزين القيم
        choices=STATUS_CHOICES,
        default='ongoing',  # الخيار الافتراضي
        verbose_name=_("الحالة"),
        help_text=_("حدد ما إذا كانت العلاقة مستمرة أو منتهية.")
    )
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات"),
        help_text=_("إضافة ملاحظات إضافية حول العلاقة (اختياري).")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text=_("مسار فريد يتم إنشاؤه تلقائيًا.")
    )
    approved = models.BooleanField(
        default=False,
        verbose_name=_("موافق عليه"),
        help_text=_("يحدد ما إذا كانت العلاقة قد تمت الموافقة عليها.")
    )
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_office_positions',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على العلاقة.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        help_text=_("الطابع الزمني عند إنشاء الوظيفة.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("آخر تحديث"),
        help_text=_("الطابع الزمني عند آخر تحديث للوظيفة.")
    )

    class Meta:
        unique_together = ('basic_info', 'office', 'is_primary', 'start_date')
        verbose_name = _("علاقة موظف بمكتب ووظيفة")
        verbose_name_plural = _("علاقات موظفين بمكاتب ووظائف")
        permissions = [
            ("can_add_employee_office_position", "يمكن إضافة علاقة موظف بمكتب ووظيفة"),
            ("can_update_employee_office_position", "يمكن تحديث علاقة موظف بمكتب ووظيفة"),
            ("can_delete_employee_office_position", "يمكن حذف علاقة موظف بمكتب ووظيفة"),
    ]

    
    
    def save(self, *args, **kwargs):
    
        if self.end_date and self.end_date <= date.today():
            self.status = 'ended'
        else:
            self.status = 'ongoing'
    
        if not self.slug and self.basic_info:
            
            slug_base = f"{self.basic_info.firstname} {self.office.name if self.office else self.basic_info.thirdname} {self.position.name if self.office else self.basic_info.secondname} "
            self.slug = slugify(unidecode(slug_base))

            # Ensure unique slugs
            original_slug = self.slug
            counter = 1
            while EmployeeOfficePosition.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)

    def get_duration(self):
        """
        حساب مدة العلاقة بين الموظف والمكتب والوظيفة.
        يقوم بحساب المدة بالسنوات والشهور والأيام.
        """
        end_date = self.end_date or date.today()  # إذا لم يكن هناك تاريخ انتهاء، يتم استخدام التاريخ الحالي
        delta = relativedelta(end_date, self.start_date)

        years = delta.years
        months = delta.months
        days = delta.days

        return years, months, days

    def __str__(self):
        """
        التمثيل النصي للكائن.
        """
        duration = self.get_duration()
        
        return f"{self.basic_info} - {self.position} في {self.office} ({'اصالة' if self.is_primary else 'ثانوي'}) - {self.status}"







############################ Log ########################
# نموذج سجل تغييرات الوحدات الإدارية
class OfficeChangeLog(models.Model):
    office = models.ForeignKey(
        Office,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("الوحدة الإدارية")
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
        verbose_name = _("سجل تغييرات الوحدات الإدارية")
        verbose_name_plural = _("سجلات تغييرات الوحدات الإدارية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.office} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات المناصب الوظيفية
class PositionChangeLog(models.Model):
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("المنصب الوظيفي")
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
        verbose_name = _("سجل تغييرات المناصب الوظيفية")
        verbose_name_plural = _("سجلات تغييرات المناصب الوظيفية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.position} - {self.action} - {self.timestamp}"

class EmployeeOfficeChangeLog(models.Model):
    employee_office = models.ForeignKey(
        EmployeeOffice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("علاقة الموظف بالدائرة")
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
        verbose_name = _("سجل تغييرات علاقة الموظف بالدائرة")
        verbose_name_plural = _("سجلات تغييرات علاقات الموظفين بالدوائر")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_office} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات علاقة موظف بمكتب ووظيفة
class EmployeeOfficePositionChangeLog(models.Model):
    employee_office_position = models.ForeignKey(
        EmployeeOfficePosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("علاقة الموظف بالمكتب والوظيفة")
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
        verbose_name = _("سجل تغييرات علاقة موظف بمكتب ووظيفة")
        verbose_name_plural = _("سجلات تغييرات علاقة موظف بمكتب ووظيفة")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_office_position} - {self.action} - {self.timestamp}"


########################## Signal ##############################

# الإشارات (Signals) الخاصة بـ Office
@receiver(pre_save, sender=Office)
def log_office_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Office.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            OfficeChangeLog.objects.create(
                office=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Office)
def log_office_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        OfficeChangeLog.objects.create(
            office=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Office)
def log_office_deletion(sender, instance, **kwargs):
    OfficeChangeLog.objects.create(
        office=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


@receiver(pre_save, sender=EmployeeOffice)
def log_employee_office_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeOffice.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeOfficeChangeLog.objects.create(
                employee_office=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


# الإشارات (Signals) الخاصة بـ Position
@receiver(pre_save, sender=Position)
def log_position_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Position.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            PositionChangeLog.objects.create(
                position=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Position)
def log_position_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        PositionChangeLog.objects.create(
            position=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Position)
def log_position_deletion(sender, instance, **kwargs):
    PositionChangeLog.objects.create(
        position=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



# الإشارات (Signals) الخاصة بـ EmployeeOfficePosition
@receiver(pre_save, sender=EmployeeOfficePosition)
def log_employee_office_position_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeOfficePosition.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeOfficePositionChangeLog.objects.create(
                employee_office_position=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EmployeeOfficePosition)
def log_employee_office_position_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeOfficePositionChangeLog.objects.create(
            employee_office_position=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EmployeeOfficePosition)
def log_employee_office_position_deletion(sender, instance, **kwargs):
    EmployeeOfficePositionChangeLog.objects.create(
        employee_office_position=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )