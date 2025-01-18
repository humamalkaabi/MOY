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
from .hr_utilities_models import DutyAssignmentOrder

from .employement_models import EmploymentHistory
from rddepartment.models.employee_education_models import EmployeeEducation
from .thanks_punishment_absence_models import EmployeePunishment, EmployeeThanks
from datetime import timedelta
from django.db.models.signals import post_migrate, pre_delete
from django.db.models.signals import pre_save, pre_delete, post_save 


class EmployeeJobTitleSettings(models.Model):
    auto_EmployeeJobTitle_upgrade = models.BooleanField(
        default=True,
        verbose_name=_("حساب العنوان الوظيفي الحالي   تلقائيا "),
        help_text=_("حدد ما إذا كانت العنوان الوظيفي الحالي يتم احتسابه تلقائيا أم لا.")
    )
    future_EmployeeJobTitle_upgrade = models.BooleanField(
        default=True,
        verbose_name=_("حساب العنوان الوظيفي القادم تلقائيا "),
        help_text=_(" حدد ما إذا كانت العنوان الوظيفي القادم يتم احتسابه تلقائيا أم لا.")
    )

    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='EmployeeJobTitlesettings',
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

    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and EmployeeJobTitleSettings.objects.exists():
            raise ValueError(_("لا يمكن إنشاء أكثر من سجل واحد لهذا النموذج."))
        super().save(*args, **kwargs)

    def get_description(self):
        return _("  يهتم هذا الجدول باعدادات احتساب العنوان الوظيفي فيما اذا كان الاحتساب تلقائيا على الجميع او يدويا. في حال تفعيله سوف يتم احتساب تغير العنوان الوظيفي بناءا على شهادة الموظف. هذا الاعداد يشمل جميع الموظفين  ")

    def delete(self, *args, **kwargs):
        # منع الحذف مع تسجيل المحاولة في السجلات
        raise ValueError(_("لا يمكن حذف هذا السجل."))

    class Meta:
        verbose_name = _("إعدادات العناوين الوظيفية ")
        verbose_name_plural = _("إعدادات العناوين الوظيفية")
        permissions = [
           
            ("can_update_employee_job_title_settings", "يمكن تحديث   اعدادات احتساب العنوان الوظيفي"),
           
        ]



@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    from django.apps import apps
    EmployeeJobTitleSettings = apps.get_model('hrhub', 'EmployeeJobTitleSettings')
    if not EmployeeJobTitleSettings.objects.exists():
        # التأكد من وجود المستخدم الافتراضي هنا
        EmployeeJobTitleSettings.objects.create(
            auto_EmployeeJobTitle_upgrade=True,
            created_by=None  # ضع المستخدم الافتراضي إذا لزم الأمر
        )

# إشارة لمنع الحذف
@receiver(pre_delete, sender=EmployeeJobTitleSettings)
def prevent_settings_deletion(sender, instance, **kwargs):
    raise ValueError(_("لا يمكن حذف هذا السجل."))



class JobTitle(MPTTModel):
    title_in_arabic = models.CharField(max_length=255, verbose_name="عنوان وظيفي")
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_titles',
        verbose_name="العنوان الوظيفي الأعلى"
    )
    description = models.TextField(blank=True, verbose_name="وصف الوظيفة")
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))

    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='job_title_created_by',
        help_text=_("المستخدم الذي قام بإنشاء أو تحديث هذه المعلومات.")
    )
    is_approved = models.BooleanField(
        default=False, 
        verbose_name=_("العنوان معتمد"), 
        help_text=_("تشير إلى ما إذا كان هذا العنوان معتمدًا.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title_in_arabic']
    def __str__(self):
        return self.title_in_arabic

    class Meta:
        ordering = ['created_at']
        verbose_name = "العنوان الوظيفي"
        verbose_name_plural = "العناوين الوظيفية"
        permissions = [
            ("can_add_job_title", "يمكن إضافة نوع عنوان وظيفي"),
            ("can_update_job_title", "يمكن تحديث نوع عنوان وظيفي"),
            ("can_delete_job_title", "يمكن حذف نوع عنوان وظيفي"),
            ("can_view_job_title", "يمكن عرض نوع عنوان وظيفي"),
        ]

    def get_description(self):
        return _("هذا يهتم بالعناوين الوظيفية وادخال البيانات وتحديثها وحذفها  ")
    
    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام title_in_arabic
        if not self.slug and self.title_in_arabic:
            self.slug = slugify(unidecode(self.title_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while JobTitle.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(JobTitle, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=EmployeeJobTitleSettings)
def update_job_titles_on_settings_change(sender, instance, **kwargs):
    # تحقق من إعدادات الاحتساب التلقائي
    if instance.auto_EmployeeJobTitle_upgrade or instance.future_EmployeeJobTitle_upgrade:
        # استرجاع جميع سجلات العناوين الوظيفية
        job_titles = EmployeeJobTitle.objects.all()
        
        for job_title in job_titles:
            # تطبيق التحديث بناءً على الإعدادات الجديدة
            job_title.auto_Employeee_upgrade = instance.auto_EmployeeJobTitle_upgrade
            job_title.save()  # استدعاء دالة الحفظ لتحديث السجلات


class EmployeeJobTitle(models.Model):
    basic_info = models.ForeignKey(
        BasicInfo,  # قم بتغيير BasicInfo إلى اسم نموذج الموظف المناسب
        on_delete=models.CASCADE,
        related_name='job_title_employee',
        verbose_name=_("الموظف"),
        help_text=_("الموظف صاحب العنوان الوظيفي  .")
    )

    auto_Employeee_upgrade = models.BooleanField(
        default=True,
        verbose_name=_("حساب العنوان الوظيفي الحالي   تلقائيا "),
        help_text=_("حدد ما إذا كانت العنوان الوظيفي الحالي يتم احتسابه تلقائيا أم لا.")
    )

    start_employee_job_title = models.ForeignKey(
        JobTitle,  # قم بتغيير Office إلى اسم نموذج المكتب المناسب
        on_delete=models.CASCADE,
         
        related_name='start_employee_job_title',
        verbose_name=_("العنوان الوظيفي عند التعين"),
        help_text=_("العنوان الوظيفي عند التعين للموظف.")
    )
    start_employee_job_title_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("تاريخ الحصول على العنوان الوظيفي  "),
        help_text=_("أدخل تاريخ الحصول على العنوان الوظيفي  .")
    )
    employee_job_title = models.ForeignKey(
        JobTitle, 
          null=True,
        blank=True, # قم بتغيير Office إلى اسم نموذج المكتب المناسب
        on_delete=models.CASCADE,
        related_name='current_employee_job_title',
        verbose_name=_("العنوان الوظيفي الحالي"),
        help_text=_("العنوان الوظيفي الحالي للموظف.")
    )
    employee_job_title_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_(" تاريخ الحصول على العنوان الوظيفي الحال  "),
        help_text=_("أدخل تاريخ الحصول على العنوان الوظيفي الحالي  .")
    )
    

    next_employee_job_title = models.ForeignKey(
        JobTitle,  # قم بتغيير Office إلى اسم نموذج المكتب المناسب
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='next_employee_job_title',
        verbose_name=_("العنوان الوظيفي القادم"),
        help_text=_("العنوان الوظيفي القادم للموظف.")
    )
    next_employee_job_title_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_(" تاريخ الحصول على العنوان الوظيفي القادم  "),
        help_text=_("أدخل تاريخ الحصول على العنوان الوظيفي القادم  .")
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات ")
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employee_job_title_created_by',
        help_text=_("المستخدم الذي قام بإنشاء أو تحديث هذه المعلومات.")
    )
    is_approved = models.BooleanField(
        default=False, 
        verbose_name=_("العنوان معتمد"), 
        help_text=_("تشير إلى ما إذا كان هذا العنوان معتمدًا.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))

    class Meta:
        verbose_name = "العنوان الوظيفي للموظف"
        verbose_name_plural = "العناوين الوظيفية للموظف "
        permissions = [
            ("can_add_employee_job_title", "يمكن إضافة  عنوان وظيفي للموظف"),
            ("can_update_employee_job_title", "يمكن تحديث  العنوان الوظيفي للموظف "),
            ("can_delete_employee_job_title", "يمكن حذف  العنوان الوظيفي للموظف "),
            ("can_view_employee_job_title", "يمكن عرض  العنوان الوظيفي للموظف "),
        ]
        indexes = [
        models.Index(fields=['is_approved', 'created_at']),
        ]
        constraints = [
        models.UniqueConstraint(
            fields=['basic_info'], 
            name='unique_employee_job_title_per_employee'
        ),
    ]


    def get_description(self):
        return _("هذا يهتم بالعناوين الوظيفية وادخال البيانات وتحديثها وحذفها  ")
    
    @classmethod
    def get_last_job_title(cls, basic_info):
        """
        هذه الدالة تقوم بإرجاع آخر عنوان وظيفي للموظف بناءً على تاريخ الإنشاء.
        """
        return cls.objects.filter(basic_info=basic_info).order_by('-created_at')
    

        
    
    def save(self, *args, **kwargs):
        if not self.slug and self.basic_info:
            self.slug = slugify(unidecode(self.basic_info.thirdname))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while EmployeeJobTitle.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        settings = EmployeeJobTitleSettings.objects.first()
        if settings and settings.auto_EmployeeJobTitle_upgrade and settings.future_EmployeeJobTitle_upgrade:
                if self.auto_Employeee_upgrade:
                    total_years = 0
                    total_months = 0
                    total_days = 0
                    if self.basic_info:
                        employment_histories = EmploymentHistory.objects.filter(
                        basic_info=self.basic_info,
                        employee_type__is_employment_type_counted=True
                        )

                        for history in employment_histories:
                            total_years += history.employee_duration_year or 0
                            total_months += history.employee_duration_month or 0
                            total_days += history.employee_duration_day or 0
                        total_months += total_days // 30
                        total_days = total_days % 30  # الأيام المتبقية
                        total_years += total_months // 12
                        total_months = total_months % 12
                        employment_history = EmploymentHistory.objects.filter(
                                basic_info=self.basic_info,
                                employee_type__is_default=True
                            ).first()
                            
                        if employment_history:
                            if not self.start_employee_job_title_date:
                                self.start_employee_job_title_date = employment_history.start_date
                        else:
                            if not self.start_employee_job_title_date:
                                self.start_employee_job_title_date = timezone.now().date()
                        latest_certificate = EmployeeEducation.get_latest_certificate(self.basic_info)
                        division_rate = (
                                latest_certificate.education_degree_type.years_effects
                                if latest_certificate and latest_certificate.education_degree_type.years_effects > 0
                                else 4  # القيمة الافتراضية
                            )
                        employment_history = employment_histories.first()
                        if employment_history and employment_history.start_date:
                            start_date = employment_history.start_date
                        else:
                            start_date = timezone.now().date()

                        
                        upgrade_grade = total_years // division_rate
                        employee_thanks = EmployeeThanks.objects.none()
                        punishments = EmployeePunishment.objects.none()
                        if upgrade_grade > 0:
                            current_upgrade_date = start_date + timedelta(days=(upgrade_grade * division_rate * 365))
                            employee_thanks = EmployeeThanks.objects.filter(emp_id_thanks=self.basic_info)
                            if employee_thanks.exists():
                                counted_thanks = employee_thanks.filter(is_counted=True)
                                valid_thanks = counted_thanks.filter(date_issued__lt=current_upgrade_date)
                                total_thanks_impact = sum(thanks.thanks_type.thanks_impact for thanks in valid_thanks)
                            else:
                                total_thanks_impact = 0
                            punishments = EmployeePunishment.objects.filter(emp_id_punishment=self.basic_info, is_counted=True)
                            if punishments.exists():
                                valid_punishments = punishments.filter(date_issued__lt=current_upgrade_date)
                                total_punishment_impact = sum(punishment.punishment_type.punishment_impact for punishment in valid_punishments)
                            else:
                                total_punishment_impact = 0

                            current_upgrade_date = current_upgrade_date - relativedelta(months=total_thanks_impact)
                            current_upgrade_date = current_upgrade_date + relativedelta(months=total_punishment_impact)
                        else:
                            current_upgrade_date = start_date


                        if self.start_employee_job_title:
                            current_job_title = self.start_employee_job_title 
                            for _ in range(upgrade_grade):
                                if current_job_title.parent:  # الانتقال إلى المستوى الأعلى
                                    current_job_title = current_job_title.parent
                                else:
                                    break
                            
                            if not self.employee_job_title:
                                self.employee_job_title = current_job_title

                        
                        if not self.employee_job_title_date or current_upgrade_date > self.employee_job_title_date:
                            self.employee_job_title_date = current_upgrade_date
                    next_upgrade_grade = upgrade_grade + 1
                    next_upgrade_date = start_date + timedelta(days=(next_upgrade_grade * division_rate * 365))
                    if employee_thanks.exists():
                        valid_thanks_future = counted_thanks.filter(
                            date_issued__gte=current_upgrade_date,
                            date_issued__lt=next_upgrade_date
                        )
                        total_thanks_impact_future = sum(thanks.thanks_type.thanks_impact for thanks in valid_thanks_future)
                    else:
                        total_thanks_impact_future = 0
                    
                    if punishments.exists():
                        valid_punishments_future = punishments.filter(
                            date_issued__gte=current_upgrade_date,
                            date_issued__lt=next_upgrade_date
                        )
                        total_punishment_impact_future = sum(
                            punishment.punishment_type.punishment_impact for punishment in valid_punishments_future
                        )
                    else:
                        total_punishment_impact_future = 0

                    next_upgrade_date = next_upgrade_date - relativedelta(months=total_thanks_impact_future)
                    next_upgrade_date = next_upgrade_date + relativedelta(months=total_punishment_impact_future)

                    
                    if self.start_employee_job_title:
                        future_job_title = self.start_employee_job_title 
                        for _ in range(next_upgrade_grade):
                            if future_job_title.parent:  # الانتقال إلى المستوى الأعلى
                                future_job_title = future_job_title.parent
                            else:
                                break
                        
                        if not self.next_employee_job_title:
                            self.next_employee_job_title = future_job_title
                        self.next_employee_job_title_date = next_upgrade_date
                
            

            
                                            
        super(EmployeeJobTitle, self).save(*args, **kwargs)
    def __str__(self):
        # التأكد من وجود البيانات قبل عرضها
        employee_name = f"{self.basic_info.firstname} {self.basic_info.secondname}" if self.basic_info else "غير معروف"
        # current_title = self.employee_job_title.title_in_arabic if self.employee_job_title else "غير محدد"
        # next_title = self.next_employee_job_title.title_in_arabic if self.next_employee_job_title else "غير محدد"
        # current_date = self.employee_job_title_date.strftime("%Y-%m-%d") if self.employee_job_title_date else "غير متوفر"
        # next_date = self.next_employee_job_title_date.strftime("%Y-%m-%d") if self.next_employee_job_title_date else "غير متوفر"

        return (
            f"الموظف: {employee_name} "
           
        )  # استدعاء الدالة save الأصلية



from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=EmployeeJobTitleSettings)
def update_job_titles_on_settings_change(sender, instance, **kwargs):
    # التأكد من أن الإعدادات تم حفظها بنجاح
    if instance.auto_EmployeeJobTitle_upgrade or instance.future_EmployeeJobTitle_upgrade:
        # الحصول على جميع سجلات العناوين الوظيفية
        employee_job_titles = EmployeeJobTitle.objects.all()
        
        for job_title in employee_job_titles:
            # هنا يمكنك التحقق إذا كانت الإعدادات تتيح التحديث التلقائي للوظائف
            if instance.auto_EmployeeJobTitle_upgrade:
                job_title.save()  # سيتم حساب العنوان الوظيفي تلقائيًا بناءً على الوظائف المنفذة في دالة `save` للموظف

            if instance.future_EmployeeJobTitle_upgrade:
                job_title.save()  # سيتم حساب العنوان الوظيفي القادم تلقائيًا بناءً على الوظائف المنفذة في دالة `save` للموظف


##################### Logs #####################
class JobTitleChangeLog(models.Model):
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("العنوان الوظيفي")
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
        verbose_name = _("سجل تغييرات العنوان الوظيفي")
        verbose_name_plural = _("سجلات تغييرات العناوين الوظيفية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.job_title} - {self.action} - {self.timestamp}"

class EmployeeJobTitleSettingsChangeLog(models.Model):
    employee_job_title_settings = models.ForeignKey(
        EmployeeJobTitleSettings,
        on_delete=models.CASCADE,
        related_name="change_logs",
        verbose_name=_("إعدادات العناوين الوظيفية"),
        help_text=_("الإعدادات المرتبطة بهذا التغيير.")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
        ],
        verbose_name=_("نوع العملية"),
        help_text=_("العملية التي تمت على السجل.")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل"),
        help_text=_("اسم الحقل الذي تم تغييره.")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة"),
        help_text=_("القيمة القديمة للحقل.")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة"),
        help_text=_("القيمة الجديدة للحقل.")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول"),
        help_text=_("المستخدم الذي قام بالتغيير.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("وقت التغيير"),
        help_text=_("الوقت الذي تم فيه التغيير.")
    )

    class Meta:
        verbose_name = _("سجل تغييرات إعدادات العناوين الوظيفية")
        verbose_name_plural = _("سجلات تغييرات إعدادات العناوين الوظيفية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_job_title_settings} - {self.action} - {self.timestamp}"
    

class EmployeeJobTitleChangeLog(models.Model):
    employee_job_title = models.ForeignKey(
        EmployeeJobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("العنوان الوظيفي للموظف"),
        help_text=_("السجل المرتبط بالتغيير.")
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'إضافة'),
            ('update', 'تعديل'),
            ('delete', 'حذف'),
        ],
        verbose_name=_("نوع العملية"),
        help_text=_("العملية التي تمت على السجل.")
    )
    field_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("اسم الحقل"),
        help_text=_("اسم الحقل الذي تم تغييره.")
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة القديمة"),
        help_text=_("القيمة القديمة للحقل.")
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("القيمة الجديدة"),
        help_text=_("القيمة الجديدة للحقل.")
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم المسؤول"),
        help_text=_("المستخدم الذي قام بالتغيير.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("وقت التغيير"),
        help_text=_("الوقت الذي تم فيه التغيير.")
    )

    class Meta:
        verbose_name = _("سجل تغييرات العنوان الوظيفي للموظف")
        verbose_name_plural = _("سجلات تغييرات العنوان الوظيفي للموظف")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_job_title} - {self.action} - {self.timestamp}"



############################ Signals ############################
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

#### Signals JobTitle ####
@receiver(pre_save, sender=JobTitle)
def log_job_title_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = JobTitle.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            JobTitleChangeLog.objects.create(
                job_title=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=JobTitle)
def log_job_title_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        JobTitleChangeLog.objects.create(
            job_title=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=JobTitle)
def log_job_title_deletion(sender, instance, **kwargs):
    JobTitleChangeLog.objects.create(
        job_title=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.models.signals import pre_save
from django.dispatch import receiver
@receiver(pre_save, sender=EmployeeJobTitle)
def log_employee_job_title_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeJobTitle.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeJobTitleChangeLog.objects.create(
                employee_job_title=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeJobTitle)
def log_employee_job_title_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeJobTitleChangeLog.objects.create(
            employee_job_title=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=EmployeeJobTitle)
def log_employee_job_title_deletion(sender, instance, **kwargs):
    EmployeeJobTitleChangeLog.objects.create(
        employee_job_title=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )



from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=EmployeeJobTitleSettings)
def log_employee_job_title_settings_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeJobTitleSettings.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeJobTitleSettingsChangeLog.objects.create(
                employee_job_title_settings=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeJobTitleSettings)
def log_employee_job_title_settings_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeJobTitleSettingsChangeLog.objects.create(
            employee_job_title_settings=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )
