import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from amazonApp.models import Category
from rest_framework import status
from collections import OrderedDict
from tests import create_category


@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestCategoriesAPI:
    
    def test_get_queryset_ok(self, create_category, api_client):
        create_category

        url = reverse('categories')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == [OrderedDict([('id', 1), ('name', 'Default Category')])]


    def test_get_queryset_no_categories(self, api_client):
        url = reverse('categories')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


   
