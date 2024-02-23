from amazonApp.models import Product, Rate
from amazonApp.serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from rest_framework.response import Response
from amazonApp.views_folder.currencies_views import provide_currency_context
from django.core.cache import cache



class ProductsAPI(APIView):

    def get(self, request, *args, **kwargs):
            
        r = self.request.query_params.get('rating')
        q = self.request.query_params.get('q')
        c = self.request.query_params.get('c')
        u = self.request.query_params.get('u')

        filters = {}
            
        if r is not None:
            filters['rating'] = float(r)
            
        if c is not None:
            filters['brands'] = c.split(",")
            
        if u is not None:
            filters['prices'] = [list(map(float, u.split("-"))) for u in u.split(",")]

        queryset = Product.objects.all()

        if q:
            queryset = queryset.filter(category_name__name__icontains=q)
            
        if filters:
            queryset = self.apply_filters(queryset, filters)

        user_id = self.kwargs.get("user_id")

        serializer = ProductSerializer(queryset, many=True, context=provide_currency_context(user_id))
        return Response(serializer.data)


    def apply_filters(self, queryset, filters):

        if "rating" in filters:
            queryset = queryset.filter(id__in=self.filter_by_rating(filters['rating']))

        if "brands" in filters:
            queryset = queryset.filter(brand__brand_name__in=filters['brands'])

        if "prices" in filters:
            currency = self.kwargs.get("currency")
            ratio = cache.get("exchange_rates")[currency] if cache.get("exchange_rates") else 1
            queryset = queryset.filter(price__range=(min([p[0]*ratio for p in filters['prices']]), max([p[1]*ratio for p in filters['prices']])))

        return queryset
    
    
    def filter_by_rating(self, rating):
        rates = Rate.objects.values("rated_products").annotate(average_rate=Avg("rate")).filter(average_rate__gte=rating)
        return [rate["rated_products"] for rate in rates]

 
    def post(self, request, *args, **kwargs):     
        try:
            lst = request.data.get("lst")
            products = []

            for product, _ in lst:
                instance = Product.objects.get(id=product)
                products.append(instance)

            serializer = ProductSerializer(products, many=True)

            return Response({"products": serializer.data})

        except Product.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
   