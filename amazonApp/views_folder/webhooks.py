from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from amazonApp.models import Product, Transaction, User, Product, CartItem
from amazonApp.serializers import CartItemSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from amazonApp.views_folder.auth_views import is_authenticated
from rest_framework.views import APIView
from django.core.cache import cache
import stripe
import random


class WebhookTransaction(APIView):

    def __init__(self):
        self.user = None
        self.product_id = None
        self.quantity = None
        self.total_price_ = 0
        self.bought = []


    @csrf_exempt
    #@is_authenticated
    def stripe_webhook(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
            )

        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            self.handle_checkout_session_completed(event)

        return HttpResponse(status=200)
    

    def handle_checkout_session_completed(self, event):
        intent = event.data.object
        location = intent.metadata.get('location', None)
        user_id = int(intent.metadata.get('user_id', None))

        self.product_id = int(intent.metadata.get('product_id', None)) if intent.metadata.get('product_id', None) else None
        self.quantity = int(intent.metadata.get('quantity', None)) if intent.metadata.get('quantity', None) else None

        try:
            self.user = User.objects.get(id=user_id)

            if location == "lobby":
                self.handle_lobby_case()

            elif location == "cart":
                self.handle_cart_case()

            self.create_transaction()

        except Exception as e:
            return Response({"error": "Failed to process the request"}, status=500)


    def random_transaction_id(self):
        while True:
            transaction_number = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
            if not Transaction.objects.filter(transaction_number=transaction_number).exists():
                break

        return transaction_number


    def handle_lobby_case(self):
        product = Product.objects.get(id=self.product_id)

        if product.quantity >= self.quantity:
            self.bought.extend([self.product.id] * self.quantity)
            product.bought_by_rec.add(self.user)

            self.total_price_ += product.price * self.quantity
            product.quantity -= self.quantity
            product.save()


    def handle_cart_case(self):
        cart_items = CartItem.objects.filter(cart__owner=self.user)
        serializer = CartItemSerializer(cart_items, many=True)

        for record in serializer.data:
            product = Product.objects.get(id=record["product"])

            if product.quantity < record["quantity"]:
                return

        for record in serializer.data:
            product = Product.objects.get(id=record["product"])

            self.bought.extend([record["product"]] * record["quantity"])
            self.total_price_ += record["total_price"]
                    
            product.bought_by_rec.add(self.user)
            product.quantity -= record["quantity"]
            product.save()

        cart_items.delete()


    def create_transaction(self):
        random_transaction_id_value = self.random_transaction_id()
    
        Transaction.objects.create(
            bought_by=self.user,
            bought_products=self.bought,
            transaction_number=random_transaction_id_value,
            total_price=self.total_price_
        )





        
