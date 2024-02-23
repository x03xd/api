import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from tests import create_product, create_user, create_brand, create_category, valid_access_token
from amazonApp.models import Product
from amazonApp.views_folder.views import Recommendations


@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestRecommendations:

    def test_get_200(self, api_client, create_product, valid_access_token):
        product = create_product

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
        
        url = reverse('recommendations', kwargs={'id': product.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK


    @patch.object(Recommendations, 'get', side_effect=Exception("Simulated error"))
    def test_get_500(self, mock_get, api_client, create_product):
        product = create_product
        
        url = reverse('recommendations', kwargs={'id': product.id})

        with pytest.raises(Exception) as exc_info:
            response = api_client.get(url)
            mock_get.assert_called_once_with(url)
            assert response.status == status.HTTP_500_INTERNAL_SERVER_ERROR

        assert str(exc_info.value) == 'Simulated error'


    @patch.object(Recommendations, 'get', side_effect=Exception("Simulated error"))
    def test_get_404(self, mock_get, api_client, create_product, valid_access_token):
        product = create_product
 
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
        url = reverse('recommendations', kwargs={'id': product.id})

        with pytest.raises(Exception) as exc_info:
            response = api_client.get(url)
            mock_get.assert_called_once_with(url)
            assert response.status == status.HTTP_404_NOT_FOUND

        assert str(exc_info.value) == 'Simulated error'