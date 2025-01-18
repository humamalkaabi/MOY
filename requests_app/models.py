from django.db import models
from personalinfo.models import BasicInfo
from accounts.models import Employee

class RequestType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

from django.utils.text import slugify

class EmployeeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المعالجة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
        ('completed', 'مكتمل'),
    ]

    # الموظف الذي يقدم الطلب
    requester = models.ForeignKey(
        BasicInfo,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name="مقدم الطلب",
        help_text="الموظف الذي أرسل الطلب."
    )

    # الموظف الذي يرد على الطلب
    responder = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,  # في حال تم حذف الموظف، لا يتم حذف الطلب
        related_name='responses',
        null=True,
        blank=True,
        verbose_name="الموظف الذي يرد على الطلب",
        help_text="الموظف المسؤول عن الرد على الطلب."
    )

    request_type = models.ForeignKey(
        RequestType,
        on_delete=models.CASCADE,
        verbose_name="نوع الطلب",
        help_text="نوع الطلب الذي يقدمه الموظف."
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان الطلب",
        help_text="عنوان موجز للطلب."
    )

    description = models.TextField(
        verbose_name="تفاصيل الطلب",
        help_text="وصف مفصل عن الطلب."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="حالة الطلب",
        help_text="تحديد حالة الطلب سواء كان قيد المعالجة، مقبول، مرفوض، إلخ."
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات",
        help_text="ملاحظات إضافية حول الطلب."
    )
    slug = models.SlugField(max_length=100,unique=True, blank=True, help_text=("سلاج فريد تم إنشاؤه للموظف (يتم إنشاؤه تلقائيًا)."))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    def __str__(self):
        return f"{self.title} "
    

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug =  slugify(self.requester.firstname)
            unique_slug = base_slug
            count = 1
            while EmployeeRequest.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{count}"
                count += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "طلب موظف"
        verbose_name_plural = "طلبات الموظفين"
        permissions = [
                ("can_resposne", "لديه القدرة على الاجابة على الطلبات      "),
                
        ]
