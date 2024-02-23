from rest_framework.serializers import ModelSerializer
from .models import Product, Category, User, Cart, Rate, Transaction, CartItem, Brand, User, Opinion
from rest_framework import serializers
from decimal import Decimal
import re
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .custom_exceptions import DuplicateUserException, DuplicateUsernameException, DuplicateEmailException


class RateSerializer(serializers.ModelSerializer):
    average_rate = serializers.FloatField()
    rated_products = serializers.CharField()
    rate_count = serializers.IntegerField()

    class Meta:
        model = Rate
        fields = ("rated_products", "average_rate", "rate_count")


class ProductRateSerializer(ModelSerializer):

    class Meta:
        model = Rate
        fields = ('rate',)

    
class GetterRateSerializer(ModelSerializer):

    class Meta:
        model = Rate
        fields = "__all__"


class StandardUserRateSerializer(ModelSerializer):

    class Meta:
        model = Rate
        fields = "__all__"


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class UserUsernameSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id')


class OpinionSerializer(serializers.ModelSerializer):
    reviewed_by = UserUsernameSerializer()
    rate = GetterRateSerializer()

    class Meta:
        model = Opinion
        fields = "__all__"


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CurrencySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["currency"]


class CartSerializer(ModelSerializer):

    class Meta:
        model = Cart
        fields = ["products"]


class ProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


    def to_representation(self, instance):
        context = self.context
        representation = super().to_representation(instance)

        if context:
            exchange_rate = context.get("user_preferred_currency") if context["user_preferred_currency"] != None else 1
            representation["price"] = round(Decimal(representation["price"]) * Decimal(exchange_rate), 2)
            
        return representation


class CartItemSerializer(ModelSerializer):

    class Meta:
        model = CartItem
        fields = "__all__"

    def to_representation(self, instance):
        context = self.context
        representation = super().to_representation(instance)

        if context:
            exchange_rate = context.get("user_preferred_currency") if context["user_preferred_currency"] != None else 1
            representation["total_price"] = round(Decimal(representation["total_price"]) * Decimal(exchange_rate), 2)
            
        return representation
    

class TransactionSerializer(ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'

    def to_representation(self, instance):
        context = self.context
        representation = super().to_representation(instance)

        if context:
            exchange_rate = context.get("user_preferred_currency") if context["user_preferred_currency"] != None else 1
            representation["total_price"] = round(Decimal(representation["total_price"]) * Decimal(exchange_rate), 2)
            
        return representation


class EditUsernameSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class EditEmailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ("email",)


class BrandsByCategoriesSerializer(ModelSerializer):

    class Meta:
        model = Brand
        fields = "__all__"


class BrandsByIdSerializer(ModelSerializer):

    class Meta:
        model = Brand
        fields = "__all__"


class CartItemProductsSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = "__all__"

    def to_representation(self, instance):
        context = self.context
        representation = super().to_representation(instance)

        if context:
            exchange_rate = context.get("user_preferred_currency") if context["user_preferred_currency"] != None else 1
            representation["total_price"] = round(Decimal(representation["total_price"]) * Decimal(exchange_rate), 2)
            
        return representation

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        email = data.get('email')
        username = data.get('username')

        if password != password2:
            raise Exception("Passwords do not match.")

        if not re.match(r'^[a-zA-Z]*$', username):
            raise Exception("Username should contain only letters.")
        
        validate_email(email)

        if User.objects.filter(email=email, username=username).exists():
            raise DuplicateUserException("A username with that username and email already exists")
        
        if User.objects.filter(username=username).exists():
            raise DuplicateUsernameException("A username with that username already exists")

        if User.objects.filter(email=email).exists():
            raise DuplicateEmailException("A username with that email already exists")

        validate_password(password)

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')

        hashed_password = make_password(password)
        user = User.objects.create(password=hashed_password, **validated_data)
        return user