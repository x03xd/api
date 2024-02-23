# Generated by Django 4.1 on 2023-07-11 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazonApp', '0003_user_password_change_allowed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='password_change_allowed',
        ),
        migrations.AlterField(
            model_name='user',
            name='email_change_allowed',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username_change_allowed',
            field=models.DateField(blank=True, null=True),
        ),
    ]