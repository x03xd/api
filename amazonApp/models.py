from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from datetime import timedelta

date = datetime.now()


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    brand_name = models.CharField(max_length=100, db_index=True)
    belongs_to_category = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return self.brand_name
    

CURRENCY_CHOICES = (
    ("USD", "USD"),
    ("EUR", "EUR"),
    ("GBP", "GBP"),
    ("PLN", "PLN")
)


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^[a-zA-Z]*$', 'Only letters are allowed.')], db_index=True)
    email = models.EmailField(max_length=30, unique=True)
    currency = models.CharField(max_length=3, null=True, default = "EUR", choices=CURRENCY_CHOICES)
    username_change_allowed = models.DateField(
        null=True,
        default=(datetime.now() + timedelta(days=30)).date()
    )
    email_change_allowed = models.DateField(
        null=True,
        default=(datetime.now() + timedelta(days=30)).date()
    )
    password_change_allowed = models.DateField(
        null=True,
        default=(datetime.now() + timedelta(days=30)).date()
    )
    groups = models.ManyToManyField(Group, related_name='amazon_users', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='amazon_users', blank=True)

    def __str__(self):
        return self.username


class Product(models.Model):
    title = models.CharField(max_length=140, db_index=True)
    description = models.CharField(max_length=1200)
    price = models.DecimalField(db_index=True, max_digits=8, decimal_places=2)
    image = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField()
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, db_index=True)
    bought_by_rec = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title


class Rate(models.Model):
    rate = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Value must be greater than or equal to 0."),
            MaxValueValidator(5, message="Value must be less than or equal to 5.")
        ], default = 0, null=True)
    rated_products = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.rated_by} has rated {self.rated_products} with {self.rate} rate"
    

class Opinion(models.Model):
    rate = models.OneToOneField(Rate, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=30)
    text = models.TextField(max_length=1200)
    reviewed_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, db_index=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    reviewed_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    test_name = models.CharField(max_length=30)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.owner)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items', db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.cart}, {self.product}, {self.quantity}"


class Transaction(models.Model):
    bought_by = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    bought_products = ArrayField(models.IntegerField())
    date = models.DateField(auto_now_add=True)
    transaction_number = models.CharField(max_length=20, unique=True, editable=False, null=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)


@receiver(post_save, sender=User)
def create_one_to_one(sender, instance, created, **kwargs):
    if created:
        one_to_one = Cart.objects.create(test_name=f"{instance}'s cart", owner=instance)
        instance.one_to_one = one_to_one
        instance.save()


@receiver(post_save, sender=Product)
def create_one_to_one(sender, instance, created, **kwargs):
    if created:
        rating = Rate.objects.create(rated_products=instance, rate=None)
        instance.rating = rating
        instance.save()
