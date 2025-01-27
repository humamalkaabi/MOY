# Generated by Django 5.1.1 on 2025-01-18 10:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rddepartment", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employeeeducation",
            name="certificat_minstery_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("education", "وزارة التربية"),
                    ("higher_education", "وزارة التعليم العالي "),
                ],
                help_text="اختر الوزارة المانحة للشهادة.",
                max_length=50,
                null=True,
                verbose_name="الوزارة المانحة",
            ),
        ),
        migrations.AlterField(
            model_name="employeeeducation",
            name="first_approved",
            field=models.BooleanField(
                blank=True,
                help_text="تشير إلى ما اذا كان القسم المسؤول عن الدراسات قد وثق الشهادة     .",
                null=True,
                verbose_name="توثيق قسم الدراسات  ",
            ),
        ),
        migrations.AlterField(
            model_name="employeeeducation",
            name="second_approved",
            field=models.BooleanField(
                blank=True,
                help_text="تشير إلى ما اذا كان القسم المسؤول عن الامور الادارية قد وثق الشهادة     .",
                null=True,
                verbose_name="توثيق  الادارية  ",
            ),
        ),
    ]
