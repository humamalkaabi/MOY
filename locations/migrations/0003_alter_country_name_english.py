# Generated by Django 5.1.1 on 2025-01-18 10:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0002_alter_country_continent_alter_country_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="name_english",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="الدولة بالإنجليزية"
            ),
        ),
    ]
