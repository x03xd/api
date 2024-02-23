from amazonApp.models import Product,  User, CartItem, Cart
from amazonApp.serializers import ProductSerializer, CartItemSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import  Sum
from decimal import Decimal
from rest_framework.response import Response
from amazonApp.views_folder.currencies_views import provide_currency_context
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from amazonApp.views_folder.auth_views import is_authenticated


class CartAPI(APIView):

    def adding_product_by_id(self, cart_item_serializer):
        product_data_list = []

        for cart_item in cart_item_serializer:
            try:
                prod = Product.objects.get(id=cart_item["product"])
                p_serializer = ProductSerializer(prod)
                
                cart_item["product_data"] = p_serializer.data
                product_data_list.append(cart_item)

            except Product.DoesNotExist as e:
                return Response({"error": "Error message", "detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        return product_data_list
    

    def counting(self, user_id):
        currency_context = provide_currency_context(user_id)

        cart = CartItem.objects.filter(cart__owner__id=user_id).order_by('product__title')
        serializer = CartItemSerializer(cart, many=True, context=currency_context)
        serializer_id = list(map(lambda item: item['product'], CartItemSerializer(cart, many=True).data))

        prod_data = self.adding_product_by_id(serializer.data)

        if currency_context["user_preferred_currency"] is None:
            currency_context["user_preferred_currency"] = 1

        sum_ = cart.aggregate(total_price_sum=Sum('total_price'))
        sum_r = round(sum_['total_price_sum'] * Decimal(currency_context["user_preferred_currency"]), 2)

        return (prod_data, sum_r, serializer_id)


    @is_authenticated
    def get(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            prod_data, sum_r, serializer_id = self.counting(user_id)

            return Response({"cart_items": prod_data, "sum": sum_r, "serialized_id": serializer_id})
                
        except (CartItem.DoesNotExist, User.DoesNotExist) as e:
            return Response({"error": "Error message", "detail": str(e)}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

    @is_authenticated
    def patch(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            product_id = request.data.get("product_id")
            quantity = request.data.get("quantity")

            product = Product.objects.get(id=product_id)
            cart = CartItem.objects.get(cart__owner__id=user_id, product=product)
                
            if product.quantity < quantity:
                return Response({"status": False, "message": "Quantity exceeds available stock", "detail": str(e)}, status=status.HTTP_200_OK)

            new_total_price = (cart.total_price * quantity) / cart.quantity

            cart.quantity = quantity
            cart.total_price = new_total_price

            cart.save()
    
            return Response({"status": True, "message": product_id})
            
        except (CartItem.DoesNotExist, Product.DoesNotExist) as e:
            return Response({"error": "Error message", "detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

    
    @is_authenticated
    def delete(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            product_id = self.kwargs['product_id']

            cart = CartItem.objects.get(cart__owner__id=user_id, product_id=product_id)
            cart.delete()

            return Response({"status": True, "product_id": product_id})

        except CartItem.DoesNotExist as e:
            return Response({"error": "Error message", "detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def validate_conditions(self, quantity, product_quantity, total_quantity):

        if quantity > product_quantity:
            return False, Response({"status": False, "info": "Quantity exceeds available stock"})

        if quantity > 10 or quantity < 1:
            return False, Response({"status": False, "info": "Quantity is not in the range of 1-10"})

        if isinstance(total_quantity, int) and total_quantity + quantity > 10:
            return False, Response({"status": False, "info": "Maximum quantity of your cart items exceeded"})

        return True, None
    
    
    def get_or_create_cart_item(self, cart, product, quantity):

        try:
            obj = CartItem.objects.get(cart=cart, product=product)
            obj.quantity += quantity
            obj.total_price += Decimal(product.price) * quantity
            obj.save()

        except CartItem.DoesNotExist:
            obj = CartItem.objects.create(
                cart = cart,
                product = product,
                quantity = quantity,
                total_price = float(product.price) * quantity
            )

    
    @is_authenticated
    def post(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 0))

            user = User.objects.get(id=user_id)
            product = Product.objects.get(id=product_id) 
            total_quantity = CartItem.objects.filter(cart__owner=user).aggregate(Sum('quantity'))['quantity__sum'] 

            valid, response = self.validate_conditions(quantity, product.quantity, total_quantity)

            if not valid:
                return response

            cart = Cart.objects.get(owner__id=user_id)  
            self.get_or_create_cart_item(cart, product, quantity)

            return Response({"status": True, "detail": "Produkt pomyślnie dodano do koszyka"})

        except (User.DoesNotExist, Product.DoesNotExist, Cart.DoesNotExist) as e:
            return Response({"error": "Object does not exist"}, status=404)    

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
