from rest_framework import status
from amazonApp.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from rest_framework.response import Response
from amazonApp.serializers import UserRegistrationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication




def is_authenticated(method):
    def wrapper(instance, request, *args, **kwargs):
        JWT_authenticator = JWTAuthentication()
        response = JWT_authenticator.authenticate(request)

        if response is not None:
            instance.kwargs['user_id'] = response[1].get('user_id')
            instance.kwargs['email'] = response[1].get('email')
            instance.kwargs['username'] = response[1].get('username')
            instance.kwargs['currency'] = response[1].get('currency')

            return method(instance, request, *args, **kwargs)
        return Response({"status": False, "error": "You have to be authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
    return wrapper


class UserData(APIView):

    @is_authenticated
    def get(self, request, *args, **kwargs):

        data = {
            "id": self.kwargs['user_id'],
            "email": self.kwargs['email'],
            "username": self.kwargs['username'],
            "currency": self.kwargs['currency'],
        }
        
        return Response({"status": True, "data": data})
        
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['currency'] = user.currency

        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user:
            update_last_login(None, user)
     
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LoginAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            username = self.kwargs.get("data")
            user_object = User.objects.get(username=username)

            return Response({'authenticated': True, 'email': user_object.email, 'username': username})
        
        except User.DoesNotExist as e:
            return Response({"error": "Error message", "detail": str(e)}, status=404)
        
        except Exception as e:
            return Response({'authenticated': False, "error": "Internal Server Error", "detail": str(e)}, status=500)


class RegisterSystem(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": True}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


        except serializers.ValidationError as e:  
            return Response({"error": "Password is too weak", "detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "An error occurred during user registration", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)