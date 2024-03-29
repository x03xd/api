# Generated by Django 4.2.4 on 2023-09-02 16:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazonApp', '0043_alter_user_email_change_allowed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_change_allowed',
            field=models.DateField(default=datetime.date(2023, 10, 2), null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password_change_allowed',
            field=models.DateField(default=datetime.date(2023, 10, 2), null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username_change_allowed',
            field=models.DateField(default=datetime.date(2023, 10, 2), null=True),
        ),
    ]
