from amazonApp.models import Product, Category, Brand
from amazonApp.serializers import ProductSerializer, CategorySerializer, BrandsByCategoriesSerializer, BrandsByIdSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.db.models import Count
from amazonApp.views_folder.currencies_views import provide_currency_context
from rest_framework import status
from amazonApp.views_folder.auth_views import is_authenticated
from django.core.cache import cache
from ..tasks import background_task


class CategoriesAPI(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset


class BrandsAPI(APIView):

    def get(self, request, *args, **kwargs):

        if 'id' in kwargs:
            return self.get_brand_by_id(self.kwargs.get('id'))
            
        elif 'category' in kwargs:
            return self.get_brands_by_category(self.kwargs.get('category'))
            
        else:
            return Response({"error": "Invalid request"}, status=400)
            

    def get_brand_by_id(self, brand_id):
        try:
            brand = Brand.objects.get(id=brand_id)
            serializer = BrandsByIdSerializer(brand)

            return Response(serializer.data)

        except Brand.DoesNotExist as e:
            return Response({"error": "Error message", "detail": str(e)}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)


    def get_brands_by_category(self, category_name):
        try:
            brands = Brand.objects.filter(belongs_to_category__name__icontains=category_name)
            serializer = BrandsByCategoriesSerializer(brands, many=True)

            return Response(serializer.data)

        except Brand.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)


class Recommendations(APIView):

    @is_authenticated
    def get(self, request, *args, **kwargs):

        try:
            username, user_id = self.kwargs['username'], self.kwargs['user_id']

            products_id = self.get_product_ids()
            recommended = self.get_recommendations(username, products_id)

            serialized = ProductSerializer(recommended, many=True, context=provide_currency_context(user_id))
                
            return Response({"recommendations": serialized.data[:5]})

        except Product.DoesNotExist:
                return Response({"error": "Object does not exist"}, status=404)    

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
            


    def get_recommendations(self, username, products_id):
        recommended = Product.objects.filter(bought_by_rec__username=username).exclude(id__in=products_id)
        recommended = recommended.annotate(freq=Count('bought_by_rec')).order_by('-freq')
        return recommended
    

    def get_product_ids(self):
        products_id = self.kwargs.get("id")
        products_id = [int(item) for item in products_id.split(", ")]
        return products_id
    
            

class LobbyPriceMod(APIView):

    def get(self, request, *args, **kwargs):

        try:
            product_id = self.kwargs.get("product_id")
            user_id = self.kwargs.get("user_id")

            product = Product.objects.get(id=product_id)
            serialized_current = ProductSerializer(product, context=provide_currency_context(user_id))

            return Response({"modified_price": serialized_current.data["price"]})

        except Product.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)    

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
       
       
