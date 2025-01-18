from django.db import models  # استيراد وحدة النماذج لإنشاء نماذج قواعد البيانات في Django
from django.utils.text import slugify  # استيراد وظيفة لتحويل النصوص إلى صيغة مناسبة لعناوين URL
from django.utils.translation import gettext_lazy as _  # استيراد وحدة الترجمة لدعم الترجمات
from django.dispatch import receiver  # استيراد وحدة استقبال الإشارات لربطها بدوال محددة
from accounts.models import Employee  # استيراد نموذج "Employee" من تطبيق "accounts" لاستخدامه
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.dispatch import receiver
from django.forms.models import model_to_dict
from accounts.models import Employee



# نموذج مجرد يحتوي على الحقول الزمنية
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تم الإنشاء في"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تم التحديث في"))

    class Meta:
        abstract = True
        verbose_name = _("نموذج الطابع الزمني")


# نموذج مجرد مع حقل slug
class SluggedModel(models.Model):
    slug = models.SlugField(
        max_length=100, unique=True, blank=True, null=True,
        verbose_name=_("الـ slug"), help_text=_("الـ slug يتم إنشاؤه تلقائيًا من الاسم إذا لم يتم توفيره")
    )

    class Meta:
        abstract = True

    def generate_unique_slug(self, name_field):
        slug_candidate = slugify(name_field)
        original_slug = slug_candidate
        counter = 1
        while self.__class__.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
            slug_candidate = f"{original_slug}-{counter}"
            counter += 1
        return slug_candidate
    

# نموذج المحافظات
class Governorate(TimestampedModel, SluggedModel):
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name=_("الموظف"))
    name_english = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name=_("المحافظة بالإنجليزية"))
    name_arabic = models.CharField(max_length=100, unique=True, verbose_name=_("المحافظة بالعربية"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    class Meta:
        verbose_name = _("المحافظة")
        verbose_name_plural = _("المحافظات")
        permissions = [
            ("can_view_governorate_details", _("عرض تفاصيل المحافظة")),
            ("can_reate_governorate", _("اضافة المحافظة")),
            ("can_update_governorate", _("تحديث المحافظة")),
            ("can_delete_governorate", _("حذف المحافظة")),
        ]

    def __str__(self):
        return self.name_arabic
    
    def get_description(self):
        return _("يتعامل هذا الجدول مع المحافظات  من حيث الاضافة والحذف والتحديث")


# نموذج المناطق
class Region(TimestampedModel, SluggedModel):
    name_english = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("الاسم بالإنجليزية"))
    name_arabic = models.CharField(max_length=100, verbose_name=_("الاسم بالعربية"))
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, verbose_name=_("المحافظة"))
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name=_("الموظف"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['governorate', 'name_english'], name='unique_region_per_governorate')
        ]
        verbose_name = _("المنطقة")
        verbose_name_plural = _("المناطق")
        permissions = [
            ("can_view_region_details", _("عرض تفاصيل المناطق")),
            ("can_create_region", _("اضافة منطقة")),
            ("can_update_region", _("تحديث منطقة")),
            ("can_delete_region", _("حذف منطقة")),
        ]

    def __str__(self):
        return f"{self.governorate.name_arabic} - {self.name_arabic}"
    
    def get_description(self):  # دالة لإرجاع وصف تفصيلي للمنطقة
        return _("يتعامل هذا الجدول مع المناطق في داخل المحافظات من حيث الإضافة والحذف والتحديث")  # وصف تفصيلي حول الغرض من النموذج


# نموذج القارات
class Continent(TimestampedModel, SluggedModel):
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name=_("الموظف"))
    name_english = models.CharField(max_length=255, unique=True, verbose_name=_("القارة بالإنجليزية"))
    name_arabic = models.CharField(max_length=255, unique=True, verbose_name=_("القارة بالعربية"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    class Meta:
        verbose_name = _("القارة")
        verbose_name_plural = _("القارات")
        ordering = ['name_english']
        permissions = [
            ("can_view_continent", _("عرض تفاصيل القارات")),
            ("can_create_continent", _(" القدرة على اضافة  قارة")),
            ("can_update_continent", _(" القدرة على تحديث القارات")),
            ("can_delete_continent", _("القدرة على حذف  القارات")),
           
        ]

    def __str__(self):
        return self.name_arabic
    
    def get_description(self):  # دالة لإرجاع وصف تفصيلي للمنطقة
        return _("يتعامل هذا الجدول مع القارات من حيث الإضافة والحذف والتحديث")  # وصف  للغرض من النموذج

# نموذج الدول
class Country(TimestampedModel, SluggedModel):
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name=_("الموظف"))
    name_english = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("الدولة بالإنجليزية"))
    name_arabic = models.CharField(max_length=255, unique=True, verbose_name=_("الدولة بالعربية"))
    description = models.TextField(null=True, blank=True, verbose_name=_("الوصف"))
    continent = models.ForeignKey(Continent, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("القارة"))

    class Meta:
        verbose_name = _("الدولة")
        verbose_name_plural = _("الدول")
        ordering = ['name_english']
        unique_together = [ 'name_arabic']
        permissions = [
            ("can_view_country_details", _("عرض تفاصيل الدول")),
            ("can_create_country", _("اضافة دول")),
            ("can_update_country", _("تحديث الدول")),
            ("can_delete_country", _("حذف الدول")),
        ]


    def __str__(self):
        return f"{self.name_arabic} ({self.name_english})"
    
    def get_description(self):  # دالة لإرجاع وصف تفصيلي للمنطقة
        return _("يتعامل هذا الجدول مع الدول من حيث الإضافة والحذف والتحديث")  # وصف  للغرض من النموذج


@receiver(pre_save, sender=Governorate)  # استقبال الإشارة لنموذج Governorate
@receiver(pre_save, sender=Region)  # استقبال الإشارة لنموذج Region
@receiver(pre_save, sender=Continent)  # استقبال الإشارة لنموذج Continent
@receiver(pre_save, sender=Country)  # استقبال الإشارة لنموذج Country
def update_slug(sender, instance, *args, **kwargs):
    """Update slug field before saving."""
    source_value = getattr(instance, 'name_english', None)  # الحصول على القيمة من الحقل name_english

    # توليد slug فقط إذا كانت القيمة موجودة
    if source_value:  # إذا كانت القيمة موجودة
        new_slug = instance.generate_unique_slug(source_value)  # توليد slug فريد
        if instance.slug != new_slug:  # إذا كان الـ slug الحالي مختلفًا عن الجديد
            instance.slug = new_slug  # تحديث قيمة الـ slug في الكائن


####################### Log changes ###################



# نموذج سجل تغييرات المحافظات
class GovernorateChangeLog(models.Model):
    governorate = models.ForeignKey(
        Governorate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات المحافظة")
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
        verbose_name = _("سجل تغييرات المحافظة")
        verbose_name_plural = _("سجلات تغييرات المحافظات")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.governorate} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات المناطق
class RegionChangeLog(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات المنطقة")
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
        verbose_name = _("سجل تغييرات المنطقة")
        verbose_name_plural = _("سجلات تغييرات المناطق")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.region} - {self.action} - {self.timestamp}"
    
# نموذج سجل تغييرات القارات
class ContinentChangeLog(models.Model):
    continent = models.ForeignKey(
        Continent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات القارة")
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
        verbose_name = _("سجل تغييرات القارة")
        verbose_name_plural = _("سجلات تغييرات القارات")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.continent} - {self.action} - {self.timestamp}"


# نموذج سجل تغييرات الدول
class CountryChangeLog(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("معلومات الدولة")
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
        verbose_name = _("سجل تغييرات الدولة")
        verbose_name_plural = _("سجلات تغييرات الدول")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.country} - {self.action} - {self.timestamp}"


########################## Signals #########################
# الإشارات (Signals) الخاصة بـ Governorate
@receiver(pre_save, sender=Governorate)
def log_governorate_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Governorate.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            GovernorateChangeLog.objects.create(
                governorate=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Governorate)
def log_governorate_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        GovernorateChangeLog.objects.create(
            governorate=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Governorate)
def log_governorate_deletion(sender, instance, **kwargs):
    GovernorateChangeLog.objects.create(
        governorate=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



        ##### Signals - Region ####
@receiver(pre_save, sender=Region)
def log_region_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Region.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            RegionChangeLog.objects.create(
                region=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Region)
def log_region_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        RegionChangeLog.objects.create(
            region=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Region)
def log_region_deletion(sender, instance, **kwargs):
    RegionChangeLog.objects.create(
        region=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )

            #### Signals Continent #######
@receiver(pre_save, sender=Continent)
def log_continent_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Continent.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            ContinentChangeLog.objects.create(
                continent=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Continent)
def log_continent_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        ContinentChangeLog.objects.create(
            continent=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Continent)
def log_continent_deletion(sender, instance, **kwargs):
    ContinentChangeLog.objects.create(
        continent=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )


            #### Signals Country ####
@receiver(pre_save, sender=Country)
def log_country_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = Country.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            CountryChangeLog.objects.create(
                country=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=Country)
def log_country_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        CountryChangeLog.objects.create(
            country=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=Country)
def log_country_deletion(sender, instance, **kwargs):
    CountryChangeLog.objects.create(
        country=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )