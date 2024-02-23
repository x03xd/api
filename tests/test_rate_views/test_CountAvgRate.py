import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from tests import create_user, create_product, create_rate, create_category, create_brand, valid_access_token
from unittest.mock import patch
from django.core.cache import cache
from amazonApp.views_folder.currencies_views import provide_currency_context


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCountAvgRate:
    
    def test_queryset_200(self, api_client):

        url = reverse('avg-rate')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK



