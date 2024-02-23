
from amazonApp.models import Product, Rate, User, Opinion
from amazonApp.serializers import RateSerializer, GetterRateSerializer, ProductRateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.db.models import Avg
from rest_framework.response import Response
from django.db.models import Count
from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_framework import status
from amazonApp.views_folder.auth_views import is_authenticated


class CountAvgRate(ListAPIView):
    serializer_class = RateSerializer

    def get_queryset(self, **kwargs):
        product_id = self.kwargs.get('product_id')
        queryset = Rate.objects.values("rated_products").annotate(average_rate=Avg("rate"), rate_count=Count("rate"))

        if product_id:
            queryset = queryset.filter(rated_products=product_id)

        return queryset
    


class RatesAPI(APIView):

    def get(self, request, *args, **kwargs):

        if "product_id" in self.kwargs:
            product_id = self.kwargs.get("product_id")
            return self.product_rate_counter(product_id)
        
        elif "user_id" in self.kwargs:
            user_id = self.kwargs.get("user_id")
            product_id = self.kwargs.get("pid")
            return self.get_rate_of_product(user_id, product_id)
        
        else:
            return Response({"error": "Invalid request"}, status=400)
            
        
    def product_rate_counter(self, product_id):
        
        try:
            result = Rate.objects.filter(rated_products__id=product_id)
            serialized_result = ProductRateSerializer(result, many=True)

            rate_frequencies = defaultdict(int)

            for data in serialized_result.data:
                rate = data['rate']
                rate_frequencies[rate] += 1

            for rate in range(1, 6):
                if rate not in rate_frequencies:
                    rate_frequencies[rate] = 0

            rate_list = [{'rate': rate, 'frequency': frequency} for rate, frequency in rate_frequencies.items()]
            sorted_rate_list = sorted(rate_list, key=lambda x: x['rate'], reverse=True)

            return Response(sorted_rate_list)

        except Rate.DoesNotExist:
            return Response({"error": "Object does not exist"})

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)


    def get_rate_of_product(self, user_id, product_id):

        try:
            rate_of_product = Rate.objects.get(rated_by__id=user_id, rated_products__id=product_id)
            serializer = GetterRateSerializer(rate_of_product)

            return Response(serializer.data["rate"])

        except Rate.DoesNotExist:
            return Response({"error": "Object does not exist"})
            
        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)


    @is_authenticated
    def patch(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        rate = self.kwargs['rate']
        product_id = self.kwargs['pid']

        try:
            product = Product.objects.get(id=product_id)
            user = User.objects.get(id=user_id)

            if not product.bought_by_rec.filter(id=user_id).exists():
                return Response({"status": False, "info": "You have to buy the product to be able to rate it"})
                
            self.create_rate(user, product, rate)

            return Response({"status": True}, status=status.HTTP_200_OK)
                    
        except (User.DoesNotExist, Product.DoesNotExist):
            return Response({"error": "Object does not exist"}, status=404)
        
        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_rate(self, user, product, rate):
        created = False

        rate_of_user, created = Rate.objects.get_or_create(
            rated_by = user,
            rated_products = product,
            defaults={'rate': rate}
        )

        if not created:
            rate_of_user.rate = rate
            rate_of_user.save()

        else:      
            opinion = get_object_or_404(Opinion, reviewed_by=user, reviewed_product=product)
            opinion.rate = rate_of_user
            opinion.save()


    @is_authenticated
    def delete(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            product_id = self.kwargs['pid']

            rate = Rate.objects.get(rated_by__id=user_id, rated_products__id=product_id)
            rate.delete()

            return Response('The rate has been restarted')
            
        except Rate.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
