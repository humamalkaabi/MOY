import os  # استيراد مكتبة os للتعامل مع نظام الملفات ونظام التشغيل
from unidecode import unidecode  # مكتبة لتحويل النصوص غير اللاتينية إلى نصوص لاتينية
from django.db import models  # استيراد النماذج (Models) لإنشاء جداول قاعدة البيانات
from django.db.models.signals import post_save, pre_save, m2m_changed  # استيراد الإشارات لمعالجة الأحداث في النماذج
from django.dispatch import receiver  # استيراد وحدة استقبال الإشارات (Signal Receiver)
from django.contrib.auth.models import AbstractUser, Group, Permission  # استيراد المستخدم الأساسي والمجموعات والصلاحيات من نظام إدارة المستخدمين
from django.contrib.auth.signals import user_logged_in, user_logged_out  # إشارات تسجيل الدخول والخروج للمستخدمين
from django.core.validators import RegexValidator  # استيراد مدقق النمط (Regex Validator) للتحقق من صحة البيانات باستخدام تعبيرات منتظمة
from django.core.exceptions import ValidationError  # استيراد خطأ التحقق من صحة البيانات
from django.core.cache import cache  # استيراد نظام التخزين المؤقت (Cache) لتخزين البيانات المؤقتة
from django.utils.text import slugify  # لتحويل النصوص إلى Slug (نصوص مختصرة وصالحة لعنوان URL)
from django.utils.translation import gettext_lazy as _  # استيراد أداة الترجمة لدعم اللغات المختلفة
from django.utils import timezone  # استيراد وحدة التعامل مع المنطقة الزمنية والتوقيت الحالي
from user_agents import parse  # مكتبة لتحليل وكشف معلومات وكيل المستخدم (User Agent)، مثل المتصفح أو الجهاز
from unidecode import unidecode  # استيراد دالة unidecode لتحويل النصوص غير اللاتينية (مثل الحروف العربية) إلى النصوص اللاتينية المقابلة
import logging  # استيراد مكتبة logging لتسجيل الأحداث (log messages) في التطبيق
from django.utils.timezone import now
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from django.utils.timezone import now


logger = logging.getLogger(__name__)  # إنشاء كائن سجل (logger) مرتبط بالملف الحالي باستخدام __name__ كاسم للسجل (هذا يسهل تتبع السجلات حسب الملف)


class Employee(AbstractUser):
    username = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9]{1,15}$',
                _('يجب إدخال اسم مستخدم يتكون من حروف أو أرقام فقط، وبطول لا يزيد عن 15.')
            )
        ],
        null=False,
        help_text=_("يجب أن يتكون اسم المستخدم من حروف وأرقام فقط، وبطول لا يزيد عن 15 حرفًا.")
    )
    groups = models.ManyToManyField(
        Group, 
        related_name='employees',
        blank=True,
        help_text=_("يمكنك إضافة الموظف إلى واحدة أو أكثر من المجموعات. يتم استخدام المجموعات لتحديد صلاحيات الوصول والمهام.")
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("صلاحيات المستخدم"),
        blank=True,
        help_text=_("صلاحيات محددة لهذا الموظف.")
    )
    is_first_login = models.BooleanField(
        default=True,
        help_text=_("يتم تعيين هذه القيمة على True عندما يقوم الموظف بتسجيل الدخول لأول مرة. يتم تحديثها بعد أول تسجيل دخول.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("فعال"),
        help_text=_("تحديد ما إذا كان حساب الموظف نشطًا أم لا. إذا كان غير نشط، لن يتمكن من تسجيل الدخول.")
    )
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees_created'
    )
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفون")
        permissions = [
            ("custom_activate_employee", "يمكن تفعيل أو إلغاء تفعيل حساب موظف"),
            ("has_register_employee_permission", " لديه الصلاحية بانشاء الحساب"),
            ("custom_view_dash_board", "يمكن  مشاهدة لوحة تحكم الموظفين ")
        ]

    def save(self, *args, **kwargs):
        # إنشاء slug فريد بناءً على اسم المستخدم
        if not self.slug or self.slug != slugify(self.username):
            base_slug = slugify(unidecode(self.username))
            unique_slug = base_slug
            counter = 1
            while Employee.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        # تعيين `is_first_login` عند إنشاء المستخدم لأول مرة
        if self._state.adding:
            self.is_first_login = True

        try:
            super().save(*args, **kwargs)
            logger.info(f"تم حفظ الموظف بنجاح: {self.username}")
        except Exception as e:
            logger.error(f"خطأ أثناء حفظ الموظف {self.username}: {e}")
            raise

    def get_description(self):
        return _("هذا الجدول يهتم بعناصر التسجيل الأساسية مثل اسم المستخدم (الرقم الوظيفي) وكلمة المرور.")

    def __str__(self):
        return self.username
    


###################### Employee Change Log ###########################


class EmployeeChangeLog(models.Model):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        verbose_name=_('Employee'),
        related_name='change_logs'
    )
    field_name = models.CharField(max_length=100, verbose_name=_('Field Name'))  # الحقل الذي تم تغييره
    old_value = models.TextField(null=True, blank=True, verbose_name=_('Old Value'))  # القيمة القديمة
    new_value = models.TextField(null=True, blank=True, verbose_name=_('New Value'))  # القيمة الجديدة
    changed_at = models.DateTimeField(default=now, verbose_name=_('Changed At'))  # وقت التغيير
    changed_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_made',
        verbose_name=_('Changed By')
    )
    change_type = models.CharField(
        max_length=50,
        choices=[
            ('create', _('انشاء')),
            ('update', _('تحديث')),
            ('delete', _('حذف')),
        ],
        verbose_name=_(' نوع التغير')
    )

    class Meta:
        verbose_name = _("سجل حركة الحسابات")
        verbose_name_plural = _("  سجلات حركة الحسابات")

    def __str__(self):
        return f"Change on {self.employee.username} - Field: {self.field_name} at {self.changed_at} by {self.changed_by}"
    


@receiver(pre_save, sender=Employee)
def log_employee_changes(sender, instance, **kwargs):
    """
    تسجيل التغييرات عند تحديث السجل.
    """
    try:
        # الحصول على النسخة القديمة من السجل (قبل التحديث)
        old_instance = Employee.objects.only('id', 'username', 'is_active', 'slug', 'password').filter(id=instance.id).first()
    except Employee.DoesNotExist:
        old_instance = None

    if old_instance:
        # الحقول التي نريد تتبع التغييرات عليها
        fields_to_track = ['username', 'is_active', 'slug', 'password']
        for field_name in fields_to_track:
            old_value = getattr(old_instance, field_name) or ""
            new_value = getattr(instance, field_name) or ""

            # تحقق من وجود تغيير في الحقل
            if old_value != new_value:
                # إنشاء سجل تغيير جديد في EmployeeChangeLog
                EmployeeChangeLog.objects.create(
                    employee=instance,
                    field_name=field_name,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    changed_at=now(),
                    changed_by=instance.created_by if instance.created_by else None,
                    change_type='update'  # نوع التغيير تحديث
                )


@receiver(pre_delete, sender=Employee)
def log_employee_deletion(sender, instance, **kwargs):
    """
    تسجيل السجل عند حذف موظف.
    """
    EmployeeChangeLog.objects.create(
        employee=instance,
        field_name='',
        old_value='',
        new_value='',
        changed_at=now(),
        changed_by=instance.created_by if instance.created_by else None,
        change_type='delete'  # نوع التغيير حذف
    )


@receiver(post_save, sender=Employee)
def log_employee_creation(sender, instance, created, **kwargs):
    """
    تسجيل السجل عند إنشاء موظف جديد.
    """
    if created:
        EmployeeChangeLog.objects.create(
            employee=instance,
            field_name='',
            old_value='',
            new_value='',
            changed_at=now(),
            changed_by=instance.created_by if instance.created_by else None,
            change_type='create'  # نوع التغيير إنشاء
        )





########################### Log in - Log out ###########################

class EmployeeActivityLog(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name='Employee'
    )
    action = models.CharField(
        max_length=20,
        choices=[('login', 'Login'), ('logout', 'Logout')],
        verbose_name='Action'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user_agent = models.CharField(max_length=255, null=True, blank=True, verbose_name='User Agent')
    browser = models.CharField(max_length=50, null=True, blank=True, verbose_name='Browser')
    operating_system = models.CharField(max_length=50, null=True, blank=True, verbose_name='Operating System')
    device = models.CharField(max_length=50, null=True, blank=True, verbose_name='Device')
    timestamp = models.DateTimeField(default=now, verbose_name='Timestamp')

    class Meta:
        verbose_name = '  سجل حركة تسجيل دخول وخروج'
        verbose_name_plural = '   سجلات حركة تسجيل دخول وخروج'
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.employee.username} - {self.action} at {self.timestamp}"
    

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    تسجيل الدخول للموظف
    """
    # تحليل User Agent
    user_agent = parse(request.META.get('HTTP_USER_AGENT', 'Unknown'))

    # استخراج التفاصيل من User Agent
    browser = user_agent.browser.family or "Unknown"
    operating_system = user_agent.os.family or "Unknown"
    device = user_agent.device.family or "Unknown"

    # الحصول على عنوان IP
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')

    # تسجيل النشاط في EmployeeActivityLog
    EmployeeActivityLog.objects.create(
        employee=user,
        action='login',
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        browser=browser,
        operating_system=operating_system,
        device=device
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    تسجيل الخروج للموظف
    """
    # تحليل User Agent
    user_agent = parse(request.META.get('HTTP_USER_AGENT', 'Unknown'))

    # استخراج التفاصيل من User Agent
    browser = user_agent.browser.family or "Unknown"
    operating_system = user_agent.os.family or "Unknown"
    device = user_agent.device.family or "Unknown"

    # الحصول على عنوان IP
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')

    # تسجيل النشاط في EmployeeActivityLog
    EmployeeActivityLog.objects.create(
        employee=user,
        action='logout',
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        browser=browser,
        operating_system=operating_system,
        device=device
    )
