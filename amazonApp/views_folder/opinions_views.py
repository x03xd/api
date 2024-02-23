
from amazonApp.models import Opinion, User, Product, Rate
from amazonApp.serializers import OpinionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from amazonApp.views_folder.auth_views import is_authenticated
from django.core.cache import cache


class OpinionsAPI(APIView):

    def get(self, request, *args, **kwargs):

        print(cache.get("exchange_rates"))

        try:
            product_id = self.kwargs.get("product_id")
            page = self.kwargs.get("page")

            opinions = Opinion.objects.filter(reviewed_product=product_id)
            opinions_in_page = opinions[page:page+5]

            serialized_data = OpinionSerializer(opinions_in_page, many=True)

            return Response({"status": True, "queryset": serialized_data.data})
            
        except Opinion.DoesNotExist as e:
            return Response({"message": "Error message", "detail": str(e)}, status=404)
            
        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
        

    @is_authenticated
    def delete(self, request, *args, **kwargs):

        try:
            opinion_id = self.kwargs['opinion_id']

            opinion = get_object_or_404(Opinion, id=opinion_id)
            opinion.delete()
                
            return Response({"status": True, "detail": "The opinion has been removed"})

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
            

    @is_authenticated
    def post(self, request, *args, **kwargs):
   
        try:
            product_id = self.kwargs['product_id']
            user_id = self.kwargs['user_id']

            user = get_object_or_404(User, id=user_id)
            product = get_object_or_404(Product, id=product_id)

            if not self.check_if_user_has_bought_product(user_id, product):
                return Response({"status": False, "detail": "You have to buy the product to be able to rate it"})
                
            if self.check_if_opinion_exists(user_id, product_id):
                return Response({"status": False, "detail": "Your opinion for this product exists already!"})
                
            text = request.data.get("text")
            title = request.data.get("title")

            if not text or not title:
                return Response({"status": False, "detail": "Make sure that title and text are not empty!"})
                
            rate = None

            try:
                rate = Rate.objects.get(rated_products=product, rated_by=user)
                    
            except:
                pass

            self.create_opinion(rate if rate else None, title, text, product, user)

            return Response({"status": True, "detail": "The opinion has been created"})

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
    def check_if_user_has_bought_product(self, user_id, product):
        return product.bought_by_rec.filter(id=user_id).exists()


    def check_if_opinion_exists(self, user_id, product_id):
        return Opinion.objects.filter(reviewed_by=user_id, reviewed_product=product_id).exists()


    def create_opinion(self, rate, title, text, product, user):
        Opinion.objects.create(
            rate=rate,
            title=title,
            text=text,
            reviewed_product=product,
            reviewed_by=user
        )

