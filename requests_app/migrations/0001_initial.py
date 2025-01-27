# Generated by Django 5.1.1 on 2025-01-18 19:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("personalinfo", "0003_alter_basicinfo_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="EmployeeRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="عنوان موجز للطلب.",
                        max_length=255,
                        verbose_name="عنوان الطلب",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="وصف مفصل عن الطلب.", verbose_name="تفاصيل الطلب"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "قيد المعالجة"),
                            ("approved", "مقبول"),
                            ("rejected", "مرفوض"),
                            ("completed", "مكتمل"),
                        ],
                        default="pending",
                        help_text="تحديد حالة الطلب سواء كان قيد المعالجة، مقبول، مرفوض، إلخ.",
                        max_length=20,
                        verbose_name="حالة الطلب",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="ملاحظات إضافية حول الطلب.",
                        null=True,
                        verbose_name="ملاحظات",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="آخر تحديث"),
                ),
                (
                    "requester",
                    models.ForeignKey(
                        help_text="الموظف الذي أرسل الطلب.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requests",
                        to="personalinfo.basicinfo",
                        verbose_name="مقدم الطلب",
                    ),
                ),
                (
                    "responder",
                    models.ForeignKey(
                        blank=True,
                        help_text="الموظف المسؤول عن الرد على الطلب.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="responses",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="الموظف الذي يرد على الطلب",
                    ),
                ),
                (
                    "request_type",
                    models.ForeignKey(
                        help_text="نوع الطلب الذي يقدمه الموظف.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="requests_app.requesttype",
                        verbose_name="نوع الطلب",
                    ),
                ),
            ],
            options={
                "verbose_name": "طلب موظف",
                "verbose_name_plural": "طلبات الموظفين",
                "permissions": [
                    ("can_resposne", "لديه القدرة على الاجابة على الطلبات      ")
                ],
            },
        ),
    ]
