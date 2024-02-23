import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from amazonApp.models import User
from rest_framework import status
from unittest.mock import patch
from tests import create_user
from rest_framework import serializers
from amazonApp.custom_exceptions import DuplicateUserException, DuplicateUsernameException, DuplicateEmailException


@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestLoginAPI:

    def test_get_201_created(self, api_client):
        
        data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'StrongPassword123',  
            'password2': 'StrongPassword123'
        }

        url = reverse('register')
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {'status': True}

    
    def test_get_500_passwords_do_not_match(self, api_client):
        
        data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'StrongPassword',  
            'password2': 'StrongPassword123'
        }

        url = reverse('register')
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {'error': 'An error occurred during user registration', 'detail': 'Passwords do not match.'}
      

    def test_get_400_weak_password(self, api_client):
        
        data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': '123',  
            'password2': '123'
        }

        url = reverse('register')
        response = api_client.post(url, data, format='json')

        print(response.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert {'error': {'non_field_errors': [serializers.ErrorDetail(string='This password is too short. It must contain at least 8 characters.',
                                                                        code='password_too_short'),
                                                                          serializers.ErrorDetail(string='This password is too common.', code='password_too_common'),
                                                                            serializers.ErrorDetail(string='This password is entirely numeric.', code='password_entirely_numeric')]}}



    def test_get_400_wrong_email_pattern(self, api_client):
        
        data = {
            'username': 'testuser',
            'email': 'testusercom',
            'password': 'StrongPassword123',  
            'password2': 'StrongPassword123'
        }

        url = reverse('register')
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'error': {'email': [serializers.ErrorDetail(string='Enter a valid email address.', code='invalid')]}}



    @pytest.mark.parametrize('exception, detail', [
        (DuplicateEmailException('A username with that email already exists'), 'A username with that email already exists'),
        (DuplicateUsernameException('A username with that username already exists'), 'A username with that username already exists'),
        (DuplicateUserException('A username with that username and email already exists'), 'A username with that username and email already exists')
    ])
    @patch('amazonApp.views_folder.auth_views.User.objects.filter')
    def test_get_500_user_exists(self, mock_post, exception, detail, api_client):
        mock_post.side_effect = exception
        
        data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'StrongPassword123',  
            'password2': 'StrongPassword123'
        }

        url = reverse('register')
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {'error': 'An error occurred during user registration', 'detail': detail}


