import pytest
from amazonApp.models import Category, Brand, Product, User, Cart, CartItem, Rate
import decimal
from rest_framework_simplejwt.tokens import AccessToken
from dotenv import main

main.load_dotenv()

@pytest.fixture
def create_category():
    category, _ = Category.objects.get_or_create(name='Default Category', id=1)
    return category


@pytest.fixture
def create_user():
    user, _ = User.objects.get_or_create(username="Default username", email="Default email")
    return user


@pytest.fixture
def create_brand(create_category):
    brand, _ = Brand.objects.get_or_create(brand_name='Default Brand', id=1, belongs_to_category=create_category)
    return brand


@pytest.fixture
def create_cart(create_user):
    cart, _ = Cart.objects.get_or_create(owner=create_user)
    if not cart.test_name:
        cart.test_name = "Default Cart"
        cart.save()
    return cart


@pytest.fixture
def create_product(create_category, create_brand, create_user):

    product, created = Product.objects.get_or_create(
        title="Default title",
        description="Default description",
        price=decimal.Decimal('100.00'),  
        image="image",
        quantity=5,
        category_name=create_category,
        brand=create_brand,
    )

    if created:
        product.bought_by_rec.add(create_user)

    return product


@pytest.fixture
def create_cartItem(create_product, create_cart):
    product = create_product
    cart = create_cart

    cartItem, _ = CartItem.objects.get_or_create(cart=cart, product=product, quantity=6, total_price=decimal.Decimal('100'))
    return cartItem


@pytest.fixture
def create_rate(create_product, create_user):
    rate, _ = Rate.objects.get_or_create(rate=3, rated_by=create_user, rated_products=create_product)
    return rate


@pytest.fixture
def valid_access_token():
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.create(
        username="ex_user",
        email="ex_user@gmail.com",
        currency="USD",
    )

    access_token = AccessToken.for_user(user)
    return str(access_token)


