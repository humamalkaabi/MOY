from django.db import models
from accounts.models import Employee
from django.core.validators import RegexValidator, EmailValidator 
from django.core.exceptions import ValidationError 
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from unidecode import unidecode  
from django.db.models.signals import post_migrate, pre_delete, post_save, pre_save

from django.dispatch import receiver

# Create your models here.



class Main_About_US(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='main_about_uS_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات  .")
    )
    title = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("عنوان الاتصال بنا"),
        help_text=_("يرجى    ادخال عبارة تعبر عن عنوان للتواصل .")
    )
    massage = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name=_(" النص المكتوب في الاتصال بنا  "),
        help_text=_("يرجى الرسالة او  النص  المكتوب في الاتصال بنا.")
    )
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        null=True, 
        blank=True, 
        validators=[RegexValidator(regex=r'^\d{11}$', message=_('يجب أن يكون رقم الهاتف 11 رقماً فقط.'))],
        help_text=_('يرجى ادخال رقم هاتف للتواصل')
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null= True,
        max_length=255,
        validators=[EmailValidator(message=_("أدخل عنوان بريد إلكتروني صحيح."))],
        help_text=_("عنوان البريد الإلكتروني  للمركز.")
    )
    locations = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("موقع المركز   "),
        help_text=_("يرجى إدخال موقع المركز  .")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم الشهادة (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('الاتصال بنا    ')
        verbose_name_plural = _('الاتصال بنا ')
        permissions = [
            ("can_create_main_about_us", _(" يمكن إنشاء نموذج الاتصال بنا وتغير الشعار")),
        ]
    def get_description(self):
        return "يتعامل هذا الجدول مع صفحة اتصال بنا."

    def save(self, *args, **kwargs):
        if not self.pk and Main_About_US.objects.exists():
            raise ValueError(_("لا يمكن إنشاء أكثر من سجل واحد لهذا النموذج."))
        super(Main_About_US, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError(_("لا يمكن حذف هذا السجل."))
    
    def __str__(self):
        return self.title
    



@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    from django.apps import apps
    Main_About_US = apps.get_model('core', 'Main_About_US')
    if not Main_About_US.objects.exists():
        Main_About_US.objects.create(
            title="اتصل بنا",
            massage="مرحبا بك في مركزنا.",
            phone_number="01234567890",
            email="example@example.com",
            locations="عنوان المركز"
        )

# إشارة لمنع الحذف
@receiver(pre_delete, sender=Main_About_US)
def prevent_settings_deletion(sender, instance, **kwargs):
    raise ValueError(_("لا يمكن حذف هذا السجل."))




######################## Log ###########################

# نموذج تسجيل الحركة
class ChangeMain_About_USLog(models.Model):
    main_about_us = models.ForeignKey(
        'Main_About_US',
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name=_("السجل المرتبط")
    )
    field_name = models.CharField(max_length=100, verbose_name=_("اسم الحقل"))
    old_value = models.TextField(blank=True, null=True, verbose_name=_("القيمة القديمة"))
    new_value = models.TextField(blank=True, null=True, verbose_name=_("القيمة الجديدة"))
    changed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("تم التغيير بواسطة")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل التغيير")
        verbose_name_plural = _("سجلات التغيير")

    def __str__(self):
        return f"{self.field_name} تغيرت في {self.timestamp}"

# إشارات لتسجيل التغييرات
@receiver(pre_save, sender=Main_About_US)
def track_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا بالفعل
        previous_instance = Main_About_US.objects.get(pk=instance.pk)
        fields_to_track = ['title', 'massage', 'phone_number', 'email', 'locations']
        
        for field in fields_to_track:
            old_value = getattr(previous_instance, field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                # قم بإضافة سجل الحركة
                ChangeMain_About_USLog.objects.create(
                    main_about_us=instance,
                    field_name=field,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=instance.created_by  # أو قم بتحديد المستخدم بشكل ديناميكي
                )


########################### Logo ####################

class Logo(models.Model):
    image = models.ImageField(
        upload_to='images/logos/', 
       
        verbose_name=_("صورة الشعار"),
        help_text=_("يرجى تحميل صورة للشعار.")
    )
    description = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        verbose_name=_("وصف الشعار"),
        help_text=_("يرجى إدخال وصف اختياري للشعار.")
    )
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("تم التحديث بواسطة")
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("تاريخ إنشاء الشعار."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("تاريخ آخر تحديث للشعار."))
    

    class Meta:
        ordering = ['created_at']
        verbose_name = _('شعار')
        verbose_name_plural = _('شعارات')

    def __str__(self):
        return self.description or _("Logo")

    def save(self, *args, **kwargs):
        if not self.pk and Logo.objects.exists():
            raise ValueError(_("لا يمكن إنشاء أكثر من سجل واحد لهذا الشعار."))
        super(Logo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError(_("لا يمكن حذف هذا الشعار."))
    
    def get_description(self):
        return _("هذا الجدول يهتم بشعار الوزارة.")
    @staticmethod
    def get_current_logo():
        return Logo.objects.last()


# إشارة لإنشاء الشعار الافتراضي بعد التهجير
@receiver(post_migrate)
def create_default_logo(sender, **kwargs):
    from django.apps import apps
    Logo = apps.get_model('core', 'Logo')
    Logo.objects.get_or_create(
        description="الشعار الافتراضي",
        defaults={
            "image": "images/logos/default_logo.png"  # صورة افتراضية
        }
    )

# إشارة لمنع الحذف
@receiver(pre_delete, sender=Logo)
def prevent_logo_deletion(sender, instance, **kwargs):
    raise ValueError(_("لا يمكن حذف هذا الشعار."))



###################### Logo log ####################

class LogoChangeLog(models.Model):
    logo = models.ForeignKey(
        'Logo', 
        on_delete=models.CASCADE, 
        related_name='change_logs', 
        verbose_name=_("الشعار")
    )
    field_name = models.CharField(max_length=100, verbose_name=_("اسم الحقل"))
    old_value = models.TextField(blank=True, null=True, verbose_name=_("القيمة القديمة"))
    new_value = models.TextField(blank=True, null=True, verbose_name=_("القيمة الجديدة"))
    changed_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("تم التغيير بواسطة")
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت التغيير"))

    class Meta:
        verbose_name = _("سجل تغيير الشعار")
        verbose_name_plural = _("سجلات تغيير الشعار")

    def __str__(self):
        return f"{self.field_name} تم تغييره في {self.timestamp}"
    
@receiver(pre_save, sender=Logo)
def track_logo_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا بالفعل
        previous_instance = Logo.objects.get(pk=instance.pk)
        fields_to_track = ['image', 'description']
        
        for field in fields_to_track:
            old_value = getattr(previous_instance, field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                # قم بإضافة سجل الحركة
                LogoChangeLog.objects.create(
                    logo=instance,
                    field_name=field,
                    old_value=old_value if old_value else _("لا توجد قيمة"),
                    new_value=new_value if new_value else _("لا توجد قيمة"),
                    changed_by=instance.created_by  # تأكد من تمرير المستخدم الذي قام بالتغيير
                )