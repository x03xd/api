from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from amazonApp.models import Product, Product, CartItem
from amazonApp.serializers import CartItemProductsSerializer, ProductSerializer
from django.core.cache import cache
from amazonApp.views_folder.auth_views import is_authenticated
from decimal import Decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeCheckout(APIView):

    def __init__(self):
        super().__init__()
        self.user_id = None
        self.location = None
        self.quantity = None
        self.product_id = None
        self.currency = "EUR"
        self.ratio = 1

    def parse_request_data(self, request, user_data):
        self.user_id = user_data['user_id']
        self.location = request.data.get("location")
        self.product_id = request.data.get("product_id", None)
        self.quantity = request.data.get("quantity", None)
        self.currency = request.data.get("currency", None)

        cache_dict = cache.get("exchange_rates")
        if cache_dict:
            self.ratio = cache_dict.get(self.currency)

        self.request.session['user_id'] = self.user_id
        self.request.session['product_id'] = self.product_id
        self.request.session['quantity'] = self.quantity
        self.request.session['location'] = self.location

    @is_authenticated
    def post(self, request, *args, **kwargs):

        try:
            self.parse_request_data(request, self.kwargs['user_id'])
            result = self.core()

            checkout_session = self.create_checkout_session(result)

            return Response({'link': checkout_session.url})
                    
        except stripe.error.StripeError as e:
            return Response(
                {'error': 'Something went wrong when creating stripe checkout session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def create_checkout_session(self, line_items):
        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={'user_id': self.user_id, 'product_id': self.product_id, 'quantity': self.quantity, 'location': self.location},
            mode='payment',
            success_url=settings.SITE_URL + '/',
            cancel_url=settings.SITE_URL + '/',
        )


    def core(self):
        if self.location == "cart":
            return self.handle_cart()
        
        if self.location == "lobby":
            return self.handle_lobby()
        
        raise Exception("Given parameter is wrong.")


    def handle_cart(self):
        try:
            cart_items = CartItem.objects.filter(cart__owner__id=self.user_id)
            serialized = CartItemProductsSerializer(cart_items, many=True)
            list_item = []

            for record in serialized.data:
                data = self.fill_data(record["product"]["price"], record["product"]["title"], record["quantity"])
                list_item.append(data)

            return list_item
        
        except CartItem.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)    

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
        
        
    def handle_lobby(self):
        try:
            product = Product.objects.get(id=self.product_id)
            serialized = ProductSerializer(product)
            list_item = []

            data = self.fill_data(serialized.data["price"], serialized.data["title"], self.quantity)
            list_item.append(data)

            return list_item
  
        except Product.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)    

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)


    def fill_data(self, price, title, quantity):
        data = {
            'price_data': {
                'currency': self.currency.lower(),
                'unit_amount': int(Decimal(price) * Decimal(self.ratio) * 100),
                'product_data': {
                    'name': title,
                },
            },
            'quantity': quantity,
        }
        return data