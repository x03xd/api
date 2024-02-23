from amazonApp.models import User
from amazonApp.serializers import CurrencySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from amazonApp.views_folder.auth_views import is_authenticated


def provide_currency_context(user_id):
    serializer_context = {}
        
    if user_id != "undefined":
        user = User.objects.get(id=user_id)
        serialized_currency = CurrencySerializer(user)
        cache_dict = cache.get("exchange_rates")

        preferred_curr = cache_dict.get(serialized_currency.data["currency"]) if cache_dict else 1
        serializer_context['user_preferred_currency'] = preferred_curr

    return serializer_context


class CurrencyConverterAPI(APIView):
    
    @is_authenticated
    def patch(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            currency = request.data.get("currency")

            if currency not in {"USD", "GBP", "PLN", "EUR"}:
                return Response({"status": False, "message": "Invalid currency choice"})

            user = User.objects.get(id=user_id)
            user.currency = currency 
            user.save()

            return Response({"status": True, "message": f"Valid currency choice: {currency}"})

        except User.DoesNotExist as e:
            return Response({"message": "Error message", "detail": str(e)}, status=404)

        except Exception as e:
            return Response({"message": "Internal Server Error", "detail": str(e)}, status=500)

