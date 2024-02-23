import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from amazonApp.models import Product, CartItem
from rest_framework import status
from unittest.mock import patch
from amazonApp.views_folder.cart_views import CartAPI


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCartAPI:

    @patch.object(CartAPI, 'post', side_effect=Exception('Simulated error'))
    def test_post_500(self, mock_post, create_product, api_client):
        product = create_product

        url = reverse('cart-create')
        data = {'product_id': product.id, 'quantity': 10}

        with pytest.raises(Exception) as exc_info:
            response = api_client.post(url, data, format='json')
            mock_post.assert_called_once_with(url)
            assert response.status == status.HTTP_500_INTERNAL_SERVER_ERROR

        assert str(exc_info.value) == 'Simulated error'


    @patch.object(CartAPI, 'post', side_effect=CartItem.DoesNotExist('Simulated error'))
    def test_post_404(self, mock_post, api_client, create_product, valid_access_token):
        product = create_product
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')

        url = reverse('cart-create')
        data = {'item_id': product.id}

        with pytest.raises(Exception) as exc_info:
            response = api_client.post(url, data, format='json')
            mock_post.assert_called_once_with(url)
            assert response.status == status.HTTP_404_NOT_FOUND

        assert str(exc_info.value) == 'Simulated error'



    def test_post_200(self, create_product, api_client, valid_access_token):
        product = create_product

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')

        url = reverse('cart-create')
        data = {'product_id': product.id, 'quantity': 1}

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": True, "detail": "Produkt pomyślnie dodano do koszyka"}



    @pytest.mark.parametrize('mock_object, exception', [
        (Product, Product.DoesNotExist('Simulating 404 status error -> no product')),
    ])
    def test_post_404(self, mock_object, exception, create_product, api_client, valid_access_token):
        with patch(f'amazonApp.views_folder.cart_views.{mock_object.__name__}.objects.get') as mock_post:
            mock_post.side_effect = exception
            product = create_product

            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')

            url = reverse('cart-create')
            data = {'product_id': product.id, 'quantity': 10}

            response = api_client.post(url, data, format='json')

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.data == {'error': 'Object does not exist'}
    


    @pytest.mark.parametrize('quantity, product_quantity, total_quantity, exception', [
        (12, 10, 3, {"status": False, "info": "Quantity exceeds available stock"}),
        (12, 13, 3, {"status": False, "info": "Quantity is not in the range of 1-10"}),
        (3, 13, 8, {"status": False, "info": "Maximum quantity of your cart items exceeded"}),
        (3, 4, 4, None),
    ])
    def test_validate_conditions(self, quantity, product_quantity, total_quantity, exception):
        instance = CartAPI()
        _, response = instance.validate_conditions(quantity, product_quantity, total_quantity)

        assert response.data if response else None == exception



    @pytest.mark.parametrize('mock_object, exception, detail', [
        (CartItem, CartItem.DoesNotExist('Simulating 404 status error -> no cartItem'), 'no cartItem'),
        (Product, Product.DoesNotExist('Simulating 404 status error -> no product'), 'no product'),
    ])
    def test_patch_404_cartItem(self, mock_object, exception, detail, api_client, create_product, create_cartItem, valid_access_token):

        with patch(f'amazonApp.views_folder.cart_views.{mock_object.__name__}.objects.get') as mock_patch:
            mock_patch.side_effect = exception

            product = create_product
            create_cartItem
            
            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
            url = reverse('cart-update')

            data = {'product_id': product.id, 'quantity': 1}
            response = api_client.patch(url, data, format='json')

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.data == {'error': 'Error message', 'detail': f'Simulating 404 status error -> {detail}'}



    @patch.object(CartAPI, 'patch', side_effect=Exception("Simulate status 500"))
    def test_patch_500(self, mock_patch, api_client, create_product, create_cartItem, valid_access_token):
        product = create_product
        create_cartItem
        
        url = reverse('cart-update')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
        
        data = {'product_id': product.id, 'quantity': 1000}

        with pytest.raises(Exception) as exc_info:
            response = api_client.patch(url, data, format='json')
            mock_patch.assert_called_once_with(url, data, format='json')
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        assert str(exc_info.value) == "Simulate status 500"



    @patch.object(CartAPI, 'delete', side_effect=Exception('Simulated error'))
    def test_delete_500(self, mock_delete, api_client, create_product, valid_access_token):
        product = create_product

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_access_token}')
        url = reverse('cart-remove', kwargs={"product_id": product.id})

        with pytest.raises(Exception) as exc_info:
           response = api_client.delete(url, format='json')
           mock_delete.assert_called_once_with(url, format='json')
           assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        assert str(exc_info.value) == "Simulated error"

