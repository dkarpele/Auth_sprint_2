# Generated by Django 4.2.1 on 2023-07-11 22:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_alter_filmwork_creation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmwork',
            name='rating',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='rating'),
        ),
    ]
