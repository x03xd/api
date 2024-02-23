# Generated by Django 4.1 on 2023-07-30 21:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazonApp', '0022_alter_rate_rated_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.IntegerField(default=0, null=True, validators=[django.core.validators.MinValueValidator(1, message='Value must be greater than or equal to 0.'), django.core.validators.MaxValueValidator(5, message='Value must be less than or equal to 5.')]),
        ),
    ]
