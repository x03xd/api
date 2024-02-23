# Generated by Django 4.1 on 2023-07-09 03:29

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=30, null=True)),
                ('coins', models.IntegerField(blank=True, null=True)),
                ('username_change_allowed', models.DateTimeField(blank=True, null=True)),
                ('email_change_allowed', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='amazon_users', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='amazon_users', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=30, null=True)),
                ('owner', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=140, null=True)),
                ('description', models.CharField(max_length=1040, null=True)),
                ('price', models.FloatField(null=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('gallery1', models.ImageField(blank=True, null=True, upload_to='')),
                ('status', models.BooleanField(blank=True, null=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='amazonApp.brand')),
                ('category_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='amazonApp.category')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bought_products', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('date', models.DateField()),
                ('bought_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1, message='Value must be greater than or equal to 0.'), django.core.validators.MaxValueValidator(5, message='Value must be less than or equal to 5.')])),
                ('rated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('rated_products', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='amazonApp.product')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='amazonApp.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazonApp.product')),
            ],
        ),
        migrations.AddField(
            model_name='brand',
            name='belong_to_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='amazonApp.category'),
        ),
    ]