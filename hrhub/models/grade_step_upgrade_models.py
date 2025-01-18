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
from .employement_models import EmploymentHistory
from .grade_step_models import EmployeeGrade, EmployeeStep
from rddepartment.models.employee_education_models import EmployeeEducation
from django.db.models import Sum
from django.utils.timezone import now

from .thanks_punishment_absence_models import EmployeeThanks, EmployeePunishment
from django.db.models.signals import post_migrate, pre_delete
from django.db.models.signals import pre_save, pre_delete, post_save  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن

class EmployeeGradeStepSettings(models.Model):
    auto_grade_step_upgrade = models.BooleanField(
        default=True,
        verbose_name=_("حساب العلاوة والترفيع تلقائيا "),
        help_text=_("حدد ما إذا كانت الدرجة أو المرحلة الوظيفية الحالية يتم حسابها تلقائيا أم لا.")
    )
    future_auto_grade_step_upgrade = models.BooleanField(
        default=True,
        verbose_name=_("حساب العلاوة والترفيع القادم تلقائيا "),
        help_text=_("حدد ما إذا كانت الدرجة أو المرحلة الوظيفية القادمة يتم حسابها تلقائيا أم لا.")
    )

    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employeegradestepsettings',
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
    class Meta:
        verbose_name = _("سجل إعدادات احتساب الدرجة والمرحلة")
        verbose_name_plural = _("سجلات إعدادات احتساب الدرجة والمرحلة")
        permissions = [
            ("can_update_employee_grade_step_settings", "يمكنه تحديث اعدادات العلاوات والترفيعات     "),
           
   ]
       

    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and EmployeeGradeStepSettings.objects.exists():
            raise ValueError(_("لا يمكن إنشاء أكثر من سجل واحد لهذا النموذج."))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # منع الحذف
        raise ValueError(_("لا يمكن حذف هذا السجل."))

    class Meta:
        verbose_name = _("إعدادات الدرجة الوظيفية")
        verbose_name_plural = _("إعدادات الدرجات الوظيفية")


@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    from django.apps import apps
    EmployeeGradeStepSettings = apps.get_model('hrhub', 'EmployeeGradeStepSettings')
    if not EmployeeGradeStepSettings.objects.exists():
        EmployeeGradeStepSettings.objects.create(
            auto_grade_step_upgrade=True,
            created_by=None  # ضع المستخدم الافتراضي إذا لزم الأمر
        )

# إشارة لمنع الحذف
@receiver(pre_delete, sender=EmployeeGradeStepSettings)
def prevent_settings_deletion(sender, instance, **kwargs):
    raise ValueError(_("لا يمكن حذف هذا السجل."))

# ####################  Logs ############################
class EmployeeGradeStepSettingsChangeLog(models.Model):
    employee_grade_step_settings = models.ForeignKey(
        EmployeeGradeStepSettings,
        on_delete=models.CASCADE,
        related_name="change_logs",
        verbose_name=_("إعدادات الدرجة الوظيفية"),
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
        verbose_name = _("سجل تغييرات إعدادات الدرجة الوظيفية")
        verbose_name_plural = _("سجلات تغييرات إعدادات الدرجة الوظيفية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_grade_step_settings} - {self.action} - {self.timestamp}"

# #################### Signals ############################
@receiver(pre_save, sender=EmployeeGradeStepSettings)
def log_employee_grade_step_settings_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeGradeStepSettings.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeGradeStepSettingsChangeLog.objects.create(
                employee_grade_step_settings=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeGradeStepSettings)
def log_employee_grade_step_settings_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeGradeStepSettingsChangeLog.objects.create(
            employee_grade_step_settings=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

###########################

class EmployeeGradeStep(models.Model):
    basic_info = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='employment_grade_step',
        verbose_name=_("الموظف")
    )
    is_initial_employment = models.BooleanField(
        default=True,
        verbose_name=_("هل هذا الموظف تعيين أولي؟"),
        help_text=_("حدد إذا كان هذا الموظف تعيينه هو الأول في المؤسسة حتى لا يتم احتساب السنة التجريبية لاغراض العلاوة والترفيع.")
    )

    start_grade = models.ForeignKey(
        EmployeeGrade,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("الدرجة الوظيفية عند بداية التعين "),
        help_text=_("الدرجة الوظيفية الموظف عند بدء العمل"),
        related_name='start_grade_employee_grade_step'
    )
    start_step = models.ForeignKey(
        EmployeeStep,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("المرحلة الوظيفية عند بداية التعين "),
        help_text=_("المرحلة الوظيفية للموظف عند بدء العمل"),
        related_name='start_step_employee_step_levels'
    )

    start_grade_date = models.DateField(
    null=True,
    blank=True,
    verbose_name=_("تاريخ بداية الدرجة عند التعيين"),
    help_text=_("التاريخ الذي بدأت فيه الدرجة الوظيفية عند التعيين.")
)

    start_step_date = models.DateField(
    null=True,
    blank=True,
    verbose_name=_("تاريخ بداية المرحلة عند التعيين"),
    help_text=_("التاريخ الذي بدأت فيه المرحلة الوظيفية عند التعيين.")
    )


    pdf_file = models.FileField(
        upload_to='employement_grade_now/',
        blank=True,
        null=True,
        verbose_name="ملف PDF",
        help_text="ملف PDF متعلق بنوع التوظيف"
    ) 
    auto_start_grade = models.BooleanField(
        default=True,
        
        verbose_name=_("ياخذ الدرجة والمرحلة عند بدايه العمل لاخر شهادة في حال توفرها"),
        help_text=_("حدد فيما اذا كنت ترغب في اخذ القيمة الاولى  للمرحلة والدرجة الوظيفية عند بداية العمل بناءا على اخر  شهادة وظيفية ")
    ) # اسم الإجازة
    auto_start_date = models.BooleanField(
        default=True,
        
        verbose_name=_("اخذ تاريخ المباشرة بالعمل هو تاريخ بداية الوظيفة الافتراضية (يوم وشهر)"),
        help_text=_("حدد فيما اذا كنت ترغب في اخذ يوم وشهر الوظيفة الافتراضية هو تاريخ بداية احتساب الدرجة والمرحلة الوظيفية ")
    ) # اسم الإجازة
    auto_grade_step_upgrade = models.BooleanField(
        default=True,
    
        verbose_name=_("حساب العلاوة والترفيع لهذا الموظف تلقائيا "),
        help_text=_("حدد ما إذا كانت الدرجة أو المرحلة الوظيفية الحالية لهذا الموظف يتم حسابها تلقائيا أم لا.")
    )
    future_auto_grade_step_upgrade = models.BooleanField(
        default=True,
        
        verbose_name=_("حساب العلاوة والترفيع القادم لهذا الموظف تلقائيا "),
        help_text=_("حدد ما إذا كانت الدرجة أو المرحلة الوظيفية القادمة لهذا الموظف يتم حسابها تلقائيا أم لا.")
    )
    

    grade_now = models.ForeignKey(
        EmployeeGrade,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("الدرجة الوظيفية الان   "),
        help_text=_("الدرجة الوظيفية الموظف الان  "),
        related_name='now_grade_employee_grade_step'
    )
    step_now = models.ForeignKey(
        EmployeeStep,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("المرحلة الوظيفية   الان "),
        help_text=_("المرحلة الوظيفية للموظف   الان"),
        related_name='now_step_employee_step_levels'
    )
    grade_temp = models.ForeignKey(
        EmployeeGrade,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("الدرجة الوظيفية مؤقتا   "),
        help_text=_("الدرجة الوظيفية الموظف مؤقتا  "),
        related_name='temp_grade_employee_grade_step'
    )
    step_temp= models.ForeignKey(
        EmployeeStep,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("المرحلة الوظيفية   موقتا "),
        help_text=_("المرحلة الوظيفية للموظف   مؤقتا"),
        related_name='temp_step_employee_step_levels'
    )


    current_grade_start_date = models.DateField(
    null=True,
    blank=True,
    verbose_name=_("تاريخ بداية الدرجة الحالية"),
    help_text=_("التاريخ الذي بدأت فيه الدرجة الوظيفية الحالية.")
    )


    total_step_grade_years = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("سنة تجريبية ")
    )
    total_step_grade_months = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("اشهر السنة التجريبية ")
    )
    total_step_grade_days = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("ايام السنة التجريبية ")
    )

    division_rate = models.PositiveIntegerField(
        null=True, blank=True, 
        verbose_name=_("سنوات الترقية  "),
        help_text= "سنوات التحول الى الدرجة الاخرى - في حال كانت فارغة فانها ياخذ القيمة المثبتة باخر شهادة للموظف وفي حال لم يكن للموظف اخر شهادة فان النظام كل 4 سنوات ويحول الدرجة"
    )
    stop_grade = models.PositiveIntegerField(
        null=True, blank=True, 
        verbose_name=_(" درجة التوقف  "),
        help_text= " درجة التوقف وفي حال تركه فارغا يتم اخذ قيمته من اخر شهادة وفي حال لم يكن متوفر في الشهادة والحقل فارغا فان القيمة تكون 1"
    )
    total_years = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("السنوات الإجمالية")
    )
    total_months = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("الشهور الإجمالية")
    )
    total_days = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("الأيام الإجمالية")
    )


    current_deserving = models.IntegerField(
        null=True, blank=True, verbose_name=_("المدة المتبقية او المدة الفائتة للاستحقاق الحالي   ")
    )
    next_deserving = models.IntegerField(
        null=True, blank=True, verbose_name=_("المدة المتبقية للاستحقاق المستقبلي ")
    )
    
    future_grade = models.ForeignKey(
    EmployeeGrade,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    verbose_name=_("الدرجة الوظيفية القادمة"),
    help_text=_("الدرجة الوظيفية التي سيتم الانتقال إليها"),
    related_name='future_grade_employee_grade_step'
    )

    future_step = models.ForeignKey(
    EmployeeStep,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    verbose_name=_("المرحلة الوظيفية القادمة"),
    help_text=_("المرحلة الوظيفية التي سيتم الانتقال إليها"),
    related_name='future_step_employee_step_levels'
    )
    

    future_effective_date = models.DateField(
    null=True,
    blank=True,
    verbose_name=_("تاريخ سريان الدرجة/المرحلة القادمة"),
    help_text=_("التاريخ المتوقع لتفعيل الدرجة أو المرحلة الوظيفية القادمة.")
    )
    


   
    STATUS_CHOICES = [
        ('approved', _("موافقة")),
        ('deserving', _("مستحق")),
        ('pending', _("انتظار")),
        ('rejected', _("رفض")),
    ]

    status = models.CharField(
        max_length=10,
        null=True,
    blank=True,
        
        choices=STATUS_CHOICES,
        default='pending',  # القيمة الافتراضية "انتظار"
        verbose_name=_("الحالة"),
        help_text=_("الحالة الحالية للسجل")
    )
    is_active = models.BooleanField(
    default=True,
    verbose_name=_("هل السجل نشط؟"),
    help_text=_("حدد ما إذا كانت الدرجة أو المرحلة الوظيفية الحالية نشطة أم لا.")
        )
    
    
    comments = models.CharField(
    max_length=255,
    null=True,
    blank=True,
    verbose_name=_("ملاحظات "),
    help_text=_("ملاحظات")
    )  
    created_by = models.ForeignKey(
        Employee,  # قم بتغيير Employee إلى النموذج المناسب
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_create_grade_step',
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
        constraints = [
            models.UniqueConstraint(fields=['basic_info'], name='unique_employee_grade_step')
        ]
        verbose_name = _('سجل الموظف الوظيفي من حيث الدرجة والمرحلة ')
        verbose_name_plural = _('سجلات الموظف الوظيفي من حيث الدرجة والمرحلة ')
        permissions = [
            ("can_add_employee_grade_step", "يمكنه اضافة ترفيعات وعلاوات        "),
             ("can_update_employee_grade_step", "يمكنه تحديث ترفيعات و علاوات الموظف        "),
              ("can_delete_employee_grade_step", "يمكنه حذف ترفيعات و علاوات الموظف        "),
           
            ]

    def calculate_total_service(self):
        total_years = 0
        total_months = 0
        total_days = 0

        if self.basic_info:
            # ✅ البحث عن السجل الأول فقط
            employment_history = EmploymentHistory.objects.filter(
                basic_info=self.basic_info,
                employee_type__is_default=True
            ).first()

            # ✅ التأكد من أن هناك سجل موجود قبل استخراج القيم
            if employment_history:
                total_years = employment_history.employee_duration_year or 0
                total_months = employment_history.employee_duration_month or 0
                total_days = employment_history.employee_duration_day or 0

            # ✅ تحديث القيم في السجل الحالي
            self.total_years = total_years
            self.total_months = total_months
            self.total_days = total_days

            # ✅ حساب المدة التجريبية
            if self.is_initial_employment:
                self.total_step_grade_years = max(0, total_years - 1)
            else:
                self.total_step_grade_years = total_years

            self.total_step_grade_months = total_months
            self.total_step_grade_days = total_days


            
    def save(self, *args, **kwargs):
        
       
        self.calculate_total_service()
       
        
        if self.basic_info:
            auto_upgrade_settings = EmployeeGradeStepSettings.objects.first()
            if auto_upgrade_settings and auto_upgrade_settings.auto_grade_step_upgrade:
                if self.auto_start_grade:
                    original_certificate = EmployeeEducation.objects.filter(
                        basic_info=self.basic_info,
                        Certificate_Type='original'
                        ).order_by('-effective_time').first()  # الحصول على أحدث شهادة تعي
                    if original_certificate and original_certificate.education_degree_type:
                        if original_certificate.education_degree_type.grade_number is not None:
                            self.start_grade = original_certificate.education_degree_type.grade_number
                
                        else:
                            self.start_grade = None
                
                        if original_certificate.education_degree_type.step_number is not None:
                            self.start_step = original_certificate.education_degree_type.step_number
                    
                    else:
                        self.start_step = None
                        self.start_step = None
            
                else:
                    if self.start_grade is not None:
                        self.start_grade = self.start_grade
                    else: 
                        self.start_grade = None
                    if self.start_step is not None:
                        self.start_step = self.start_step
                    else: 
                        self.start_step = None
                
                employment_history = EmploymentHistory.objects.filter(
                        basic_info=self.basic_info,
                        employee_type__is_default=True
                    ).first()
                if employment_history:
                    if self.auto_start_date:
                        self.start_grade_date = employment_history.start_date
                        self.start_step_date = employment_history.start_date
                    else:
                        if self.start_grade_date is not None:
                            self.start_grade_date = self.start_grade_date
                            self.start_step_date = self.start_step_date
                        else:
                            self.start_grade_date = None
                            self.start_step_date = None
                
                if self.auto_grade_step_upgrade:
                    # print("OK Now")
                    total_years = EmploymentHistory.objects.filter(
                        employee=self.basic_info,
                        employee_type__is_default=True
                        ).aggregate(
                        total_years=Sum('employee_duration_year')
                        )['total_years'] or 0
                    self.current_grade_start_date = self.start_grade_date.replace(
                            year=self.start_grade_date.year + total_years)
                    # print("total_years:", total_years)
                    # print("self.current_grade_start_date:", self.current_grade_start_date)

                    employee_thanks = EmployeeThanks.objects.filter(emp_id_thanks=self.basic_info)
                    counted_thanks = EmployeeThanks.objects.filter(emp_id_thanks=self.basic_info, is_counted=True)
                    valid_thanks = counted_thanks.filter(date_issued__lt=self.current_grade_start_date)
                    total_thanks_impact = sum(thanks.thanks_type.thanks_impact for thanks in valid_thanks)
                    punishments = EmployeePunishment.objects.filter(emp_id_punishment=self.basic_info, is_counted=True)
                    valid_punishments = punishments.filter(date_issued__lt=self.current_grade_start_date)
                    total_punishment_impact = sum(punishment.punishment_type.punishment_impact for punishment in valid_punishments)
                    self.current_grade_start_date = self.current_grade_start_date  - relativedelta(months=total_thanks_impact) + relativedelta(months=total_punishment_impact)
                    latest_certificate = EmployeeEducation.get_latest_certificate(self.basic_info)
                    if self.division_rate is None:
                        if latest_certificate:
                            if latest_certificate.education_degree_type.years_effects:
                                division_rate = latest_certificate.education_degree_type.years_effects
                                self.division_rate = division_rate
                            else: 
                                division_rate = 4
                                self.division_rate  = division_rate
                        
                        else:
                            division_rate = 4
                            self.division_rate = division_rate
                    else: 
                        division_rate = self.division_rate
                    
                    if self.stop_grade is None:
                        if latest_certificate:
                            if latest_certificate.education_degree_type.stop_point:
                                stop_grade = latest_certificate.education_degree_type.stop_point
                            else:
                                stop_grade = 1
                        
                        else:
                            stop_grade = 1
                    else:
                        stop_grade = self.stop_grade

                    upgrade_grade = self.total_step_grade_years // division_rate
                    remaining_years = self.total_step_grade_years % division_rate
                    # print("upgrade_grade", upgrade_grade)
                    if self.start_grade:
                        new_grade_number = self.start_grade.grade_number - upgrade_grade
                        new_grade_number = min(new_grade_number, stop_grade)
                        self.grade_now = EmployeeGrade.objects.filter(grade_number=new_grade_number).first()
                    if self.grade_now:
                        if (upgrade_grade > 0):
                            step_number = remaining_years
                        else: 
                            step_number = self.start_step.step_number + remaining_years
                        valid_steps = EmployeeStep.objects.filter(grade_number=self.grade_now)
                        current_step = valid_steps.filter(step_number=step_number).first()
                        if not current_step:
                            current_step = valid_steps.first()
                        self.step_now = current_step
                        
                    # print("remaining_years", remaining_years)
                    if self.future_auto_grade_step_upgrade:
                        if self.grade_now and self.step_now:
                            future_total_years = self.total_step_grade_years + 1
                            future_upgrade_grade = future_total_years // division_rate
                            future_remaining_years = future_total_years % division_rate
                            future_grade_number = self.start_grade.grade_number - future_upgrade_grade
                            future_grade_number = max(future_grade_number, stop_grade)
                            self.future_grade = EmployeeGrade.objects.filter(grade_number=future_grade_number).first()
                            if self.future_grade:
                                if future_upgrade_grade > 0:
                                    future_step_number = future_remaining_years
                                else:
                                    future_step_number = self.start_step.step_number + future_remaining_years
                                
                                future_valid_steps = EmployeeStep.objects.filter(grade_number=self.future_grade)
                                future_step = future_valid_steps.filter(step_number=future_step_number).first() or future_valid_steps.first()
                                self.future_step = future_step
                        if self.current_grade_start_date:
                            
                            future_grade_start_date = self.current_grade_start_date + relativedelta(years=1)
                            self.future_effective_date = future_grade_start_date
                            employee_thanks = EmployeeThanks.objects.filter(emp_id_thanks=self.basic_info)
                            counted_thanks = employee_thanks.filter(is_counted=True)
                            valid_thanks_future = counted_thanks.filter(date_issued__gte=self.current_grade_start_date, date_issued__lt=future_grade_start_date)
                            total_thanks_impact_future = sum(thanks.thanks_type.thanks_impact for thanks in valid_thanks_future)
                            punishments = EmployeePunishment.objects.filter(emp_id_punishment=self.basic_info, is_counted=True)
                            valid_punishments_future = punishments.filter(date_issued__gte=self.current_grade_start_date, date_issued__lt=future_grade_start_date)
                            total_punishment_impact_future = sum(punishment.punishment_type.punishment_impact for punishment in valid_punishments_future)
                            self.future_effective_date = self.future_effective_date - relativedelta(months=total_thanks_impact_future) + relativedelta(months=total_punishment_impact_future)
        
        if self.current_grade_start_date:
            today = date.today()
            remaining_time = self.current_grade_start_date - today
            self.current_deserving = remaining_time.days  # يتم حساب الفرق بالأيام
        else:
            self.current_deserving = None

        if not self.slug and self.basic_info:
            self.slug = slugify(unidecode(f"{self.basic_info.firstname}-{self.basic_info.thirdname}"))

        if self.future_effective_date:
            today = date.today()
            remaining_time = self.future_effective_date - today
            self.next_deserving = remaining_time.days  # يتم حساب الفرق بالأيام
        else:
            self.next_deserving = None

        # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while EmployeeGradeStep.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

       
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"المعلومات الوظيفية: {self.basic_info}"





from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=EmployeeEducation)
@receiver(post_delete, sender=EmployeeEducation)
def update_employee_grade_step(sender, instance, **kwargs):
    # الحصول على الموظف المرتبط بالشهادة
    employee = instance.basic_info

    # جلب السجل المرتبط بـ EmployeeGradeStep
    employee_grade_step = EmployeeGradeStep.objects.filter(employee=employee).first()

    if employee_grade_step:
        # الحصول على الشهادة الأحدث
        latest_certificate = EmployeeEducation.get_latest_certificate(employee)

        if latest_certificate and latest_certificate.education_degree_type:
            # تحديث الدرجة الوظيفية بناءً على نوع الشهادة
            if latest_certificate.education_degree_type.grade_number is not None:
                employee_grade_step.start_grade = latest_certificate.education_degree_type.grade_number
            else:
                employee_grade_step.start_grade = None

        # حفظ التغييرات في السجل الوظيفي
        employee_grade_step.save()


@receiver(post_save, sender=EmployeeGradeStepSettings)
def update_employee_grade_steps(sender, instance, **kwargs):
    """
    تحديث سجلات EmployeeGradeStep عند تعديل EmployeeGradeStepSettings.
    """
    auto_upgrade = instance.auto_grade_step_upgrade
    future_auto_upgrade = instance.future_auto_grade_step_upgrade

    # تحديث السجلات في EmployeeGradeStep بناءً على القيم الجديدة
    employee_grade_steps = EmployeeGradeStep.objects.all()
    for grade_step in employee_grade_steps:
        grade_step.auto_grade_step_upgrade = auto_upgrade
        grade_step.future_auto_grade_step_upgrade = future_auto_upgrade
        grade_step.save()


@receiver(post_save, sender=EmployeePunishment)
def update_employee_grade_step(sender, instance, **kwargs):
    # احصل على قائمة الموظفين الذين تأثروا بالعقوبة
    punished_employees = instance.emp_id_punishment.all()

    for employee in punished_employees:
        # تحقق من وجود سجل للموظف في EmployeeGradeStep
        grade_step = EmployeeGradeStep.objects.filter(employee=employee).first()
        if grade_step:
            # تحديث الحقول حسب المنطق المطلوب
            grade_step.total_days = (grade_step.total_days or 0) - 1  # مثال للتعديل
            grade_step.save()


@receiver(post_save, sender=EmployeeThanks)
def update_employee_grade_step_on_thanks(sender, instance, **kwargs):
    """
    يتم استدعاء هذه الإشارة عند إنشاء أو تحديث سجل جديد في EmployeeThanks
    لتطبيق تأثير الشكر على EmployeeGradeStep.
    """
    # احصل على قائمة الموظفين المستهدفين من الشكر
    thanked_employees = instance.emp_id_thanks.all()

    for employee in thanked_employees:
        # تحقق من وجود سجل في EmployeeGradeStep للموظف
        grade_step = EmployeeGradeStep.objects.filter(employee=employee).first()
        if grade_step:
            # قم بتطبيق تأثير الشكر (thanks_impact) من نوع الشكر
            impact = instance.thanks_type.thanks_impact
            
            # تعديل الحقول المناسبة بناءً على التأثير
            grade_step.total_days = (grade_step.total_days or 0) + impact  # مثال لتأثير إيجابي
            grade_step.save()

@receiver(pre_save, sender=EmployeeThanks)
def track_date_issued_change(sender, instance, **kwargs):
    try:
        old_instance = EmployeeThanks.objects.get(pk=instance.pk)
        if old_instance.date_issued != instance.date_issued:
            print(f"تم تغيير date_issued من {old_instance.date_issued} إلى {instance.date_issued}")
            thanked_employees = instance.emp_id_thanks.all()
            for employee in thanked_employees:
                grade_step = EmployeeGradeStep.objects.filter(employee=employee).first()
                if grade_step:
                    grade_step.start_step_date = instance.date_issued
                    grade_step.save()
    except EmployeeThanks.DoesNotExist:
        # السجل جديد
        print("تم إنشاء سجل جديد")




######################## Log ####################
class EmployeeGradeStepChangeLog(models.Model):
    employee_grade_step = models.ForeignKey(
        EmployeeGradeStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("سجل درجة ومرحلة الموظف"),
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
        verbose_name = _("سجل تغييرات درجة ومرحلة الموظف")
        verbose_name_plural = _("سجلات تغييرات درجة ومرحلة الموظف")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee_grade_step} - {self.action} - {self.timestamp}"



###################################### Signal ################################################

@receiver(pre_save, sender=EmployeeGradeStep)
def log_employee_grade_step_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EmployeeGradeStep.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EmployeeGradeStepChangeLog.objects.create(
                employee_grade_step=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )

@receiver(post_save, sender=EmployeeGradeStep)
def log_employee_grade_step_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EmployeeGradeStepChangeLog.objects.create(
            employee_grade_step=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )

@receiver(post_delete, sender=EmployeeGradeStep)
def log_employee_grade_step_deletion(sender, instance, **kwargs):
    EmployeeGradeStepChangeLog.objects.create(
        employee_grade_step=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )
