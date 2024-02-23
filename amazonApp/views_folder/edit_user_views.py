
from rest_framework import status
from amazonApp.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import JsonResponse
from datetime import timedelta, date
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
import re
from rest_framework.response import Response
from amazonApp.views_folder.auth_views import is_authenticated


class EditUsername(APIView):

    @is_authenticated
    def patch(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            change = request.data.get("change")

            user = User.objects.get(id=user_id)
            today_date = date.today()

            if user.username_change_allowed >= today_date:
                return Response({"error": f"You cannot change username till {user.username_change_allowed}"})
                
            if not re.match(r'^[a-zA-Z]+$', change):
                return Response({"error": "Username should contain only letters."})

            if User.objects.filter(username=change).exists():
                return Response({"error": "User with passed username already exists"})
                
            user.username = change

            new_date = date.today() + timedelta(days=30) 
            user.username_change_allowed = new_date
            user.save()

            return Response({"status": True})

        except User.DoesNotExist as e:
            return Response({"error": "Error message", "detail": str(e)}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)

    

class EditEmail(APIView):

    @is_authenticated
    def patch(self, request, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            change = request.data.get("change")

            user = User.objects.get(id=user_id)
            today_date = date.today()

            if user.email_change_allowed >= today_date:
                return Response({"error": f"You cannot change email till {user.email_change_allowed}"})
                
            validate_email(change)

            if User.objects.filter(email=change).exists():
                return Response({"error": "User with passed email already exists"})
                
            user.email = change

            new_date = date.today() + timedelta(days=30) 
            user.email_change_allowed = new_date
            user.save()

            return Response({"status": True})

        except User.DoesNotExist as e:
            return Response({"error": "Error message", "detail": str(e)}, status=404)

        except ValidationError as e:
            return Response({"error": "Email format is not correct", "detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": "An error occurred during user registration", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EditPassword(APIView):

    @is_authenticated
    def patch(self, request, *args, **kwargs):

        try:
            user_id = self.kwargs['user_id']
            current = request.data.get("current")
            password = request.data.get("password")
            password2 = request.data.get("password2")

            user = User.objects.get(id=user_id)
            today_date = date.today()

            if user.password_change_allowed >= today_date:
                return Response({"error": f"You cannot change password till {user.username_change_allowed}"})

            password_matches = check_password(current, user.password)

            if not password_matches:
                return Response({"error": "Your current password is not correct"})

            if password != password2:
                return Response({"error": "Passwords do not match."})
                
            validate_password(password)

            hashed_password = make_password(password)
            user.password = hashed_password

            new_date = today_date + timedelta(days=30) 
            user.password_change_allowed = new_date

            user.save()

            return Response({"status": True})

        except User.DoesNotExist as e:
            return JsonResponse({"error": "Error message", "detail": str(e)}, status=404)

        except ValidationError as e:
            return Response({"error": "Password is too weak", "detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": "An error occurred during user registration", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
       

class AccessToChangeStatus(APIView):
    
    @is_authenticated
    def get(self, request, *args, **kwargs):

        today_date = date.today()

        try:
            user_id = self.kwargs['user_id']
            user = User.objects.get(id=user_id)

            if user.username_change_allowed >= today_date:
                status_username = False

            elif user.username_change_allowed < today_date:
                status_username = True


            if user.email_change_allowed >= today_date:
                status_email = False

            elif user.email_change_allowed < today_date:
                status_email = True


            if user.password_change_allowed >= today_date:
                status_password = False

            elif user.password_change_allowed < today_date:
                status_password = True

            return Response({
                "username": [status_username, user.username_change_allowed],
                "email": [status_email, user.email_change_allowed],
                "password": [status_password, user.password_change_allowed]
            })

        except User.DoesNotExist:
            return Response({"error": "Object does not exist"}, status=404)

        except Exception as e:
            return Response({"error": "Internal Server Error", "detail": str(e)}, status=500)
            
