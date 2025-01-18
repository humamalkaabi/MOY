import calendar
import logging
import re
import threading
import time
from collections import defaultdict
from datetime import datetime, date, timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from unidecode import unidecode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from accounts.models import Employee
from mptt.models import MPTTModel, TreeForeignKey
from personalinfo.models import BasicInfo
from django.db.models import Sum

from django.utils.timezone import now

# إعداد الـ logging
logger = logging.getLogger(__name__)



def leave_type_path(instance, filename):
    # استخدام اسم الإجازة مع معالجة الحروف غير المسموح بها
    leave_name = instance.name if instance.name else "unknown_leave"
    clean_name = re.sub(r'[^\w\s-]', '_', leave_name.strip())  # استبدال الحروف غير المسموح بها
    return f"leave_documents/leave_types/{clean_name}/documents/{filename}"

class LeaveType(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False) 
     # اسم الإجازة
    is_balance_based = models.BooleanField(default=True,
                                            verbose_name="هل تعتمد على الرصيد   ",
                                           help_text="هل يعتمد هذه النوع على الرصيد")
    
   
    accepts_negative_numbers = models.BooleanField(default=False,
                                            verbose_name="هل يقبل الرقم السالب؟",
                                            help_text ="يرجى تحديد فيما اذا كان هذا النوع يقبل الرقم السالب وفي حال عدم الاختيار فانه يرفض الرقم السالب ")  # هل تعتمد على الرصيد؟
    
    max_days_per_year = models.DecimalField(
        max_digits=10,  
        decimal_places=2,  
        null=True, blank=True,
        verbose_name="عدد الايام بالسنة",
        help_text="يرجى اختيار اقصى مقدار للرصيد السنوي "
        )  # الحد الأقصى من الأيام سنويًا
    monthly_increment = models.DecimalField(
        max_digits=10,  # إجمالي عدد الأرقام (بما في ذلك الأرقام بعد العلامة العشرية)
        decimal_places=2,  # 
        null=True, blank=True,
        verbose_name="مقدار الزيادة شهريا",
        help_text="يرجى اختيار رقم زيادة الرصيد شهريا في حال كان النوع يعتمد على الرصيد")
    
    
    LEAVE_CHOICES = [
        ('FullPAID', 'يستحق راتب مع كافة مخصصاته '),
        ('PAID', 'إجازة  مع راتب اسمي ومخصصات ثابتة'),
        ('SpecialPAID', ' إجازة  مع راتب اسمي ومخصصات ثابته ومخصصات اجازة'),
        ('UNPAID', 'إجازة بدون راتب'),
        ('OTHER', 'آخر'),
        ]
    
    leave_paid_type = models.CharField(
        max_length=100, 
        choices=LEAVE_CHOICES, 
        default='FullPAID',
        verbose_name=_("نوع الإجازة المدفوعة"),
        help_text=_("نوع الإجازة المدفوعة أو غير المدفوعة.")
        )
    leave_type_document = models.FileField(
        upload_to=leave_type_path,
        null=True,
        blank=True,
        verbose_name="السند القانوني -اختياري",
        help_text="وثيقة أو القانون الخاص بهذا النوع من الإجازة.",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )

    comments = models.TextField(
            null=True, 
            blank=True, 
            verbose_name="ملاحظات - اختياري   ",
            help_text=_("وصف مختصر لنوع الإجازة - اختياري - يمكن إضافة ملاحظات إضافية.")
            )

    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_LeaveType',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على ادخال البيانات.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("آخر تحديث"),
        help_text=_(" تاريخ اخر تحديث .")
    )
    slug = models.SlugField(max_length=50,unique=True, blank=True, null=True, verbose_name="Slug")
    class Meta:
        verbose_name = "نوع الاجازة  "
        verbose_name_plural = "انواع الاجازات  "
        permissions = [
            ("can_add_leave_type", "يمكن إضافة نوع اجازة"),
            ("can_update_leave_type", "يمكن تحديث نوع الاجازة"),
            ("can_delete_leave_type", "يمكن حذف نوع الاجازة"),
            ("can_view_leave_type", "يمكن عرض نوع الاجازة"),
        ]

    def get_description(self):
        return _("يهتم هذا الجدول بالتعامل مع انواع الاجازات التي تعطي للموظفين من حيث اسم الاجازة والسند القانوني لها وهل تعتمد على الرصيد وغيرها من التفاصيل     ")
   

    def save(self, *args, **kwargs):

        if not self.is_balance_based:
            self.is_balance_based = False
        
        if not self.accepts_negative_numbers:
            self.accepts_negative_numbers = False
        
        if not self.max_days_per_year:
            self.max_days_per_year = 36
        
        if not self.monthly_increment:
            self.monthly_increment = 3

        if not self.slug and self.name:
        # تنظيف الاسم وإزالة الحروف الغير لائقة
            clean_name = unidecode(self.name)
            self.slug = slugify(clean_name)

        # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while LeaveType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super(LeaveType, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    


class LeaveBalance(models.Model):
    employee = models.ForeignKey(BasicInfo, on_delete=models.CASCADE, related_name="employee_leave_balances")
    old_balance = models.DecimalField(
        max_digits=10,  # إجمالي عدد الأرقام (بما في ذلك الأرقام بعد العلامة العشرية)
        decimal_places=2,
        default=0, null=True, blank=True,
        verbose_name="   الرصيد القديم")  # القيمة الأساسية
    balance = models.DecimalField(
        max_digits=10,  # إجمالي عدد الأرقام (بما في ذلك الأرقام بعد العلامة العشرية)
        decimal_places=2,
        default=0.0,  # قيمة افتراضية
        null=True,
        blank=True
        )  # القيمة الأساسية
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="NewNumber_leave_balances")
    start_date = models.DateField(
        null=True, blank=True, help_text="بداية انشاء رصيد الاجازات للموظف في حال تركه فارغا فانه سوف ياخذ تاريخ اليوم",
        verbose_name="تاريخ بداية انشاء الرصيد"
    )
    last_updated = models.DateTimeField(
        auto_now=True,  # تغيير إلى auto_now لتحديث الوقت تلقائيًا عند كل حفظ
        verbose_name=_("آخر تحديث"),
        help_text=_("آخر وقت تم فيه تحديث الرقم.")
    )
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_leave_balance',
        verbose_name=_("أنشئ بواسطة"),
        help_text=_("الموظف الذي أنشأ أو وافق على ادخال البيانات.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("آخر تحديث"),
        help_text=_("الطابع الزمني عند آخر تحديث للبيانات.")
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name="Slug")

    previous_start_date = None  # لتخزين `start_date` السابق

    class Meta:
        verbose_name = _("رصيد الاجازات ")
        verbose_name_plural = _("رصيد الاجازات ")
        constraints = [
            models.UniqueConstraint(fields=['employee', 'leave_type'], name='unique_leave_balance_per_employee')
        ]
        permissions = [
            ("can_add_leave_balance", "يمكن إضافة  رصيد اجازة للموظف"),
            ("can_update_leave_balance", "يمكن تحديث  رصيد اجازة الموظف"),
            ("can_delete_leave_balance", "يمكن حذف  رصيد اجازة الموظف"),
            ("can_view_leave_balance", "يمكن عرض  رصيد اجازة الموظف"),
        ]


    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = now().date()
        
        if not self.old_balance:
            self.old_balance = 0.0

        if not self.balance:
            self.balance = 0.0
            
        today = now().date()

        months_passed = (today.year - self.start_date.year) * 12 + (today.month - self.start_date.month)
        #print("months_passed", months_passed)
        self.balance = months_passed * self.leave_type.monthly_increment + self.old_balance

        if self.employee and self.leave_type:
            leave_requests = LeaveRequest.objects.filter(employee=self.employee, leave_type=self.leave_type, status='Approved')
        else:
            leave_requests = []
            
        total_days_used = sum([request.total_duration_days for request in leave_requests])
        self.balance -= total_days_used
        #print(" self.balance",  self.balance)
        
        if not self.slug and self.employee:
        # إنشاء base_slug باستخدام بيانات مختصرة
            base_slug = f"{self.employee.firstname}-{self.employee.secondname[:1]}-{self.leave_type.name[:3]}-{self.start_date}"
            base_slug = slugify(unidecode(base_slug))
        
        # التأكد من تفرد slug
            original_slug = base_slug
            counter = 1
            while LeaveBalance.objects.filter(slug=base_slug).exists():  # التحقق من LeaveBalance بدلاً من LeaveType
                base_slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = base_slug


        super(LeaveBalance, self).save(*args, **kwargs)


class LeaveRequest(models.Model):
    employee = models.ForeignKey(BasicInfo, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="leave_requests")
    start_date = models.DateField(null=False, blank=False, verbose_name="تاريخ بداية الإجازة", help_text="تاريخ بداية الإجازة")
    end_date = models.DateField(null=False, blank=False, verbose_name="تاريخ نهاية الإجازة", help_text="تاريخ نهاية الإجازة")
    duration_years = models.IntegerField(null=True, blank=True, verbose_name="مدة الإجازة بالسنوات", help_text="مدة الإجازة بالسنوات")
    duration_months = models.IntegerField(null=True, blank=True, verbose_name="مدة الإجازة بالشهور", help_text="مدة الإجازة بالشهور")
    duration_days = models.IntegerField(null=True, blank=True, verbose_name="مدة الإجازة بالأيام", help_text="مدة الإجازة بالأيام")
    total_duration_days = models.IntegerField(null=True, blank=True, verbose_name="المدة الاجمالية الإجازة بالأيام", help_text="المدة الاجمالية الإجازة بالأيام")
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'قيد الانتظار'), ('Approved', 'موافقة'), ('Rejected', 'مرفوض')],
        default='Pending',
        verbose_name="حالة الإجازة"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_leave_requests', verbose_name="أنشئ بواسطة", help_text="الموظف الذي قام بإنشاء الطلب")
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name="Slug")

    class Meta:
        verbose_name = "طلب إجازة"
        verbose_name_plural = "طلبات الإجازة"
        permissions = [
            ("can_add_leave_request", "يمكن إضافة  اجازة للموظف"),
            ("can_update_leave_request", "يمكن تحديث اجازة الموظف  "),
            ("can_delete_leave_request", "يمكن حذف   اجازة الموظف"),
            ("can_view_leave_request", "يمكن عرض اجازة الموظف  "),
        ]

    def save(self, *args, **kwargs):

        if self.start_date and self.end_date:
            delta = relativedelta(self.end_date, self.start_date)
            

            self.duration_years = delta.years
            self.duration_months = delta.months
            self.duration_days = delta.days +  1

            self.total_duration_days = (self.end_date - self.start_date).days + 1
            

            # print("self.total_duration_days",self.total_duration_days)
        
        if self.leave_type.is_balance_based:
            leave_balance = LeaveBalance.objects.get(employee=self.employee, leave_type=self.leave_type)
            if self.total_duration_days > leave_balance.balance and self.leave_type.accepts_negative_numbers == False:
                raise ValidationError(f"لا  يوجد لديك رصيد كافي ")
            
        
            if self.status == 'Approved':
                
                # print("leave_balance.balance", leave_balance.balance)
                leave_balance.balance -= self.total_duration_days
                # print("leave_balance.balance", leave_balance.balance)
                leave_balance.save()
        
        if not self.slug and self.employee:
        # إنشاء base_slug باستخدام بيانات مختصرة
            base_slug = f"{self.employee.firstname}-{self.employee.secondname[:4]}-{self.leave_type.name[:2]}"
            base_slug = slugify(unidecode(base_slug))
        
        # التأكد من تفرد slug
            original_slug = base_slug
            counter = 1
            while LeaveRequest.objects.filter(slug=base_slug).exists():  # التحقق من LeaveBalance بدلاً من LeaveType
                base_slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = base_slug

        super(LeaveRequest, self).save(*args, **kwargs)
    def get_status_display_ar(self):
        status_dict = {
            'Pending': 'قيد الانتظار',
            'Approved': 'موافقة',
            'Rejected': 'مرفوض',
        }
        return status_dict.get(self.status, self.status)
    
   

    def __str__(self):
        return f"إجازة {self.leave_type.name} للموظف {self.employee.firstname} {self.employee.secondname} من {self.start_date} إلى {self.end_date}"



@receiver(post_save, sender=LeaveRequest)
def update_leave_balance_on_approval(sender, instance, created, **kwargs):
    """
    تحديث رصيد الإجازة تلقائيًا عند الموافقة على طلب الإجازة.
    """
    if instance.leave_type.is_balance_based and instance.status == 'Approved':
        # الحصول على أو إنشاء سجل رصيد الإجازة
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee=instance.employee,
            leave_type=instance.leave_type,
            defaults={
                'old_balance': 0,
                'balance': 0,
                'start_date': now().date(),
                'created_by': instance.created_by,
            }
        )

        # تحديث الرصيد بناءً على المدة الإجمالية للإجازة
        leave_balance.balance -= instance.total_duration_days
        leave_balance.save()

from django.db.models.signals import post_delete


@receiver(post_delete, sender=LeaveRequest)
def restore_leave_balance_on_delete(sender, instance, **kwargs):
    """
    إعادة تحديث رصيد الإجازة عند حذف طلب الإجازة.
    """
    # التحقق من أن نوع الإجازة يعتمد على الرصيد
    if instance.leave_type.is_balance_based and instance.status == 'Approved':
        try:
            # الحصول على رصيد الإجازة للموظف ونوع الإجازة
            leave_balance = LeaveBalance.objects.get(employee=instance.employee, leave_type=instance.leave_type)
            # إعادة المدة الإجمالية للإجازة إلى الرصيد
            leave_balance.balance += instance.total_duration_days
            leave_balance.save()
        except LeaveBalance.DoesNotExist:
            # إذا لم يكن هناك سجل رصيد، يمكن تجاهل العملية
            pass

############################ Logs ######################
class LeaveTypeChangeLog(models.Model):
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات نوع الإجازة")
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
        verbose_name = _("سجل تغييرات نوع الإجازة")
        verbose_name_plural = _("سجلات تغييرات أنواع الإجازة")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.leave_type} - {self.action} - {self.timestamp}"


class LeaveBalanceChangeLog(models.Model):
    leave_balance = models.ForeignKey(
        LeaveBalance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("رصيد الإجازة")
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
        verbose_name = _("سجل تغييرات رصيد الإجازة")
        verbose_name_plural = _("سجلات تغييرات أرصدة الإجازات")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.leave_balance} - {self.action} - {self.timestamp}"
    
class LeaveRequestChangeLog(models.Model):
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("طلب الإجازة")
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
        verbose_name = _("سجل تغييرات طلب الإجازة")
        verbose_name_plural = _("سجلات تغييرات طلبات الإجازة")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.leave_request} - {self.action} - {self.timestamp}"


################################## Signal ###########################
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=LeaveType)
def log_leave_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = LeaveType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            LeaveTypeChangeLog.objects.create(
                leave_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=LeaveType)
def log_leave_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        LeaveTypeChangeLog.objects.create(
            leave_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=LeaveType)
def log_leave_type_deletion(sender, instance, **kwargs):
    LeaveTypeChangeLog.objects.create(
        leave_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=LeaveBalance)
def log_leave_balance_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = LeaveBalance.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            LeaveBalanceChangeLog.objects.create(
                leave_balance=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=LeaveBalance)
def log_leave_balance_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        LeaveBalanceChangeLog.objects.create(
            leave_balance=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=LeaveBalance)
def log_leave_balance_deletion(sender, instance, **kwargs):
    LeaveBalanceChangeLog.objects.create(
        leave_balance=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )




from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=LeaveRequest)
def log_leave_request_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = LeaveRequest.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            LeaveRequestChangeLog.objects.create(
                leave_request=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=LeaveRequest)
def log_leave_request_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        LeaveRequestChangeLog.objects.create(
            leave_request=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=LeaveRequest)
def log_leave_request_deletion(sender, instance, **kwargs):
    LeaveRequestChangeLog.objects.create(
        leave_request=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )
