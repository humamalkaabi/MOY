from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from unidecode import unidecode
from accounts.models import Employee
# Content types
from hrhub.models.grade_step_models import EmployeeGrade, EmployeeStep
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete  # استيراد الإشارة pre_save التي يتم استخدامها لتنفيذ العمليات قبل حفظ الكائن

# Create your models here.


class EducationDegreeType(models.Model):
    created_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='education_degree_type_created_by',
        help_text=_("المستخدم الذي قام بإنشاء هذه المعلومات الخاصة بالمدرسة.")
    )
    name_in_arabic = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("اسم الشهادة العلمية بالعربية"),
        help_text=_("يرجى إدخال اسم الشهادة بالعربية.")
    )
    name_in_english = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("اسم الشهادة العلمية بالانكليزية"),
        help_text=_("يرجى إدخال اسم الشهادة بالانكليزية.")
    )

    grade_number = models.ForeignKey(
    EmployeeGrade,
    on_delete=models.SET_NULL,  # اجعلها SET_NULL لضمان إمكانية تعيينها إلى NULL عند حذف الدرجة
    blank=True,  # يسمح بترك الحقل فارغًا في النماذج
    null=True,  # يسمح بتخزين القيمة NULL في قاعدة البيانات
    related_name="education_degrees",
    verbose_name=_("الدرجة الوظيفية"),
    help_text=_("الدرجة الوظيفية المرتبطة بهذه الشهادة.")
            )
    step_number = models.ForeignKey(
     EmployeeStep,
    on_delete=models.SET_NULL,  # اجعلها SET_NULL لضمان إمكانية تعيينها إلى NULL عند حذف المرحلة
    blank=True,  # يسمح بترك الحقل فارغًا في النماذج
    null=True,  # يسمح بتخزين القيمة NULL في قاعدة البيانات
    related_name="education_degrees",
    verbose_name=_("المرحلة الوظيفية"),
    help_text=_("المرحلة الوظيفية المرتبطة بهذه الشهادة.")
    )
    education_degree_number = models.PositiveIntegerField(
    blank=True,
    null=True,
    verbose_name=_("مستوى الشهادة"),
    validators=[
        MinValueValidator(1, message="رقم مستوى الشهادة يجب أن يكون 1 أو أعلى")
    ],
    help_text=_("يرجى إدخال مستوى الشهادة. هذا الحقل مفيد لغرض احتساب الشهادة المضافة - يبدأ هذا الحقل تصاعديًا من 1 فما فوق.")
)
    
    years_effects = models.PositiveIntegerField(
    blank=True,
    null=True,
    default=0,
     verbose_name=_(" سنوات الترفيع "),
    help_text="ادخال تاثير هذا النوع على عدد سنوات الترفيع في الحالات الطبيعية بدون اضافة شهادة"
    )
    stop_point = models.PositiveIntegerField(
    blank=True,
    null=True,
    default=1,
    help_text="ادخل الدرجة الوظيفية التي يتوقف عندها صاحب الشهادة "
    )

    
    has_effect = models.BooleanField(
        default=False,
        
        verbose_name=_("تاثيره في الشهادات المضافة "),
        help_text=_("تحديد ما إذا كان لهذا النوع من الشهادات تأثير على الدرجة  الوظيفية وسنوات الترفيع في حالة الشهادات المضافة .")
    )
   
    addtion_years_effects = models.PositiveIntegerField(
    blank=True,
    null=True,
    default=0,
    verbose_name=_(" سنوات التسريع في حال الشهادة المضافة   "),
    help_text="ادخال تاثير الشهادة المضافة من هذا النوع على عدد السنوات"
    )

    comments = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("ملاحظات عن الشهادة الدراسية او الاكاديمية"),
        help_text=_("ملاحظات عن الشهادة الدراسية او الاكاديمية")
    )

    slug = models.SlugField(unique=True, blank=True, help_text=_("سلاج فريد تم إنشاؤه للاسم الشهادة (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("التوقيت الذي تم فيه إنشاء السجل."))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("التوقيت الذي تم فيه تحديث السجل آخر مرة."))
    class Meta:
        ordering = ['created_at']
        verbose_name = _('نوع الشهادة الدراسية ')
        verbose_name_plural = _('أنواع الشهادات الدراسية')
        permissions = [
            ("can_add_education_degree_type", "يمكن اضافة اسم ونوع  الشهادة الاكاديمية"),
            ("can_update_education_degree_type", "يمكن تحديث اسم ونوع الشهادة الاكاديمية  "),
            ("can_delete_education_degree_type", "يمكن حذف اسم ونوع الشهادة الاكاديمية "),
                ]

    def get_description(self):
        return "يتعامل هذا الجدول مع اسم نوع الشهادة الدراسية او الاكاديمية مثل  يقرا ويكتب او دبلوم او بكالوريوس او غيرها."

    def save(self, *args, **kwargs):
        # تحقق من وجود الـ slug وإذا لم يكن موجودًا، يتم إنشاؤه باستخدام name_in_arabic
        if not self.slug and self.name_in_arabic:
            self.slug = slugify(unidecode(self.name_in_arabic))

            # التحقق من وجود slug مكرر
            original_slug = self.slug
            counter = 1
            while EducationDegreeType.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super(EducationDegreeType, self).save(*args, **kwargs)  # استدعاء الدالة save الأصلية

    def __str__(self):
        return self.name_in_arabic
    

##################### Logs ####################

# نموذج سجل تغييرات أنواع الشهادات الدراسية
class EducationDegreeTypeChangeLog(models.Model):
    education_degree_type = models.ForeignKey(
        EducationDegreeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_logs",
        verbose_name=_("نوع الشهادة الدراسية")
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
        verbose_name = _("سجل تغييرات نوع الشهادة الدراسية")
        verbose_name_plural = _("سجلات تغييرات أنواع الشهادات الدراسية")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.education_degree_type} - {self.action} - {self.timestamp}"

############### Signal ########################


# الإشارات (Signals) الخاصة بـ EducationDegreeType
@receiver(pre_save, sender=EducationDegreeType)
def log_education_degree_type_changes(sender, instance, **kwargs):
    if instance.pk:  # إذا كان السجل موجودًا مسبقًا
        previous = EducationDegreeType.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field_name, None)
            new_value = getattr(instance, field_name, None)

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        for field_name, old_value, new_value in changes:
            EducationDegreeTypeChangeLog.objects.create(
                education_degree_type=instance,
                action="update",
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                user=instance.created_by,  # المستخدم المسؤول
            )


@receiver(post_save, sender=EducationDegreeType)
def log_education_degree_type_creation(sender, instance, created, **kwargs):
    if created:  # إذا كان السجل جديدًا
        EducationDegreeTypeChangeLog.objects.create(
            education_degree_type=instance,
            action="create",
            user=instance.created_by,  # المستخدم المسؤول
        )


@receiver(post_delete, sender=EducationDegreeType)
def log_education_degree_type_deletion(sender, instance, **kwargs):
    EducationDegreeTypeChangeLog.objects.create(
        education_degree_type=None,  # السجل المحذوف
        action="delete",
        user=instance.created_by,  # المستخدم المسؤول
    )