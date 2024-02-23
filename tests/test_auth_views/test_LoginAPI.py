import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from amazonApp.models import User
from rest_framework import status
from unittest.mock import patch
from tests import create_user, valid_access_token
from amazonApp.views_folder.auth_views import LoginAPI, is_authenticated
from rest_framework.response import Response


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestLoginAPI:

    def test_get_200(self, api_client, create_user):
        user = create_user

        url = reverse('login', kwargs={'data': user.username})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'authenticated': True, 'email': 'Default email', 'username': 'Default username'}


    @patch.object(LoginAPI, 'get', side_effect=User.DoesNotExist('Simulated error'))
    def test_get_404(self, mock_get, api_client, create_user):
        user = create_user

        url = reverse('login', kwargs={'data': user.username})

        with pytest.raises(Exception) as exc_info:
            response = api_client.get(url)
            mock_get.assert_called_once_with(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND

        assert str(exc_info.value) == 'Simulated error'




    @patch.object(LoginAPI, 'get', side_effect=Exception('Simulated error'))
    def test_get_500(self, mock_get, api_client, create_user):
        user = create_user

        url = reverse('login', kwargs={'data': user.username})

        with pytest.raises(Exception) as exc_info:
            response = api_client.get(url)
            mock_get.assert_called_once_with(url)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        assert str(exc_info.value) == 'Simulated error'