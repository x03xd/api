from amazonApp.models import Product, Transaction, User
from amazonApp.serializers import ProductSerializer, TransactionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from amazonApp.views_folder.currencies_views import provide_currency_context
from collections import Counter
from amazonApp.views_folder.auth_views import is_authenticated


class TransactionsAPI(APIView):

    @is_authenticated
    def get(self, request, *args, **kwargs):

        user_id = self.kwargs['user_id']
        
        if "year" in self.kwargs:
            year = self.kwargs.get("year")
            return self.get_transactions_by_year(year, user_id)

        elif "products_id" in self.kwargs:
            products_id = self.kwargs.get("products_id")
            return self.get_transaction_products(products_id, user_id)
        
        else:
            return Response({"error": "Invalid request"}, status=400)
            

    def get_transactions_by_year(self, year, user_id):

        try:
            user = User.objects.get(id=user_id)

            queryset = Transaction.objects.filter(bought_by=user, date__year=year)
            serialized = TransactionSerializer(queryset, many=True, context=provide_currency_context(user_id))

            return Response(serialized.data)
               
        except Transaction.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)


    def get_transaction_products(self, products_id, user_id):

        try:
            products_id = products_id.split(",")
            products_id = [int(product_id) for product_id in products_id]
                
            table = Counter()

            for x in products_id:
                table[x] += 1

            products = Product.objects.filter(id__in=products_id)
            serialized = ProductSerializer(products, many=True, context=provide_currency_context(user_id))

            for product in serialized.data:
                product["count"] = table[product["id"]]

            return Response(serialized.data)
            
        except Product.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
