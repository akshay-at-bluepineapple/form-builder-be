# Generated by Django 5.2.1 on 2025-05-23 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jsonformapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="column",
            name="column_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="row",
            name="row_name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
