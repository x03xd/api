import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from tests import create_user, valid_access_token
from unittest.mock import patch
from django.core.cache import cache
from amazonApp.serializers import CurrencySerializer
from amazonApp.views_folder.currencies_views import provide_currency_context, CurrencyConverterAPI

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_provide_currency_context(create_user):
    
    exchange_rates = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.75,
    }
    cache.set("exchange_rates", exchange_rates)
    
    user = create_user
    serializer_context = provide_currency_context(user.id)
    
    assert 'user_preferred_currency' in serializer_context
    
    currency_serializer = CurrencySerializer(user)
    expected_currency = exchange_rates[currency_serializer.data['currency']]
    
    assert serializer_context['user_preferred_currency'] == expected_currency


@pytest.mark.django_db
class TestCurrencyConverterAPI:
    
    def test_patch_200(self, api_client, valid_access_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')

        url = reverse('currency-converter')  
        data = {'currency': 'USD'}

        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": True, "message": f"Valid currency choice: USD"}



    def test_patch_curreny_unavaiable(self, api_client, valid_access_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')

        url = reverse('currency-converter')  
        data = {'currency': 'BUF'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({"status": False, "message": "Invalid currency choice"})



    @patch.object(CurrencyConverterAPI, 'patch', side_effect=Exception('Simulated error'))
    def test_patch_500(self, mock_patch, api_client):

        url = reverse('currency-converter')  
        data = {'currency': 'USD'}

        with pytest.raises(Exception) as exc_info:
            api_client.patch(url, data, format='json')
            mock_patch.assert_called_once_with(url, data, format='json')
            
        assert str(exc_info.value) == 'Simulated error'



    def test_patch_401(self, api_client):

        url = reverse('currency-converter')  
        data = {'currency': 'USD'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {'status': False, 'error': 'You have to be authenticated'}
       

