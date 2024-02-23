from django.contrib import admin
from .models import User, Cart, Product, Category, Rate, Transaction, CartItem, Brand, Opinion

admin.site.register(User)
admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Rate)
admin.site.register(Transaction)
admin.site.register(CartItem)
admin.site.register(Brand)
admin.site.register(Opinion)