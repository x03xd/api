from django.urls import path

from amazonApp.views_folder import views
from amazonApp.views_folder import auth_views
from amazonApp.views_folder import rate_views
from amazonApp.views_folder import edit_user_views
from amazonApp.views_folder import cart_views
from amazonApp.views_folder import currencies_views
from amazonApp.views_folder import transactions_views
from amazonApp.views_folder import filter_products_views
from amazonApp.views_folder import opinions_views
from amazonApp.views_folder import payments_views
from amazonApp.views_folder import webhooks
from rest_framework_simplejwt.views import TokenVerifyView
from amazonApp.views_folder.auth_views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    #PRODUCTS FILTER
    path("products/<user_id>/<currency>/", filter_products_views.ProductsAPI.as_view()),

    #AUTHENTICATION
    path("registration/", auth_views.RegisterSystem.as_view(), name="register"),
    path("login/<data>", auth_views.LoginAPI.as_view(), name="login"),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-user/', auth_views.UserData.as_view()),

    #RATE
    path('avg-rate/', rate_views.CountAvgRate.as_view(), name="avg-rate"),
    path('avg-rate/<product_id>/', rate_views.CountAvgRate.as_view(), name='single-avg-rate'),

    path('rate-product/update/<pid>/<rate>', rate_views.RatesAPI.as_view(), name='rate-update'),
    path('rate-product/delete/<pid>', rate_views.RatesAPI.as_view(), name='rate-remove'),
    
    path('rate-product/id/<user_id>/<pid>/', rate_views.RatesAPI.as_view(), name='rate-by-id'),
    path('rate-product/frequency/<product_id>/', rate_views.RatesAPI.as_view(), name='rate-freq'),

    #OPINION
    path('opinions/<str:product_id>/<int:page>/', opinions_views.OpinionsAPI.as_view(), name='opinions'),
    path('opinions/create/<int:product_id>', opinions_views.OpinionsAPI.as_view(), name='opinion-create'),
    path('opinions/remove/<int:opinion_id>', opinions_views.OpinionsAPI.as_view(), name='opinion-remove'),

    #USER_EDIT
    path("edit-username/", edit_user_views.EditUsername.as_view()),
    path("edit-email/", edit_user_views.EditEmail.as_view()),
    path("change-password/", edit_user_views.EditPassword.as_view()),
    path("access-to-change-status/", edit_user_views.AccessToChangeStatus.as_view()),

    #CART
    path("cart/create/", cart_views.CartAPI.as_view(), name="cart-create"),
    path("cart/remove/<int:product_id>/", cart_views.CartAPI.as_view(), name="cart-remove"),
    path("cart/update/", cart_views.CartAPI.as_view(), name="cart-update"),

    #TRANSACTIONS
    path("transactions/list/<year>/", transactions_views.TransactionsAPI.as_view()),
    path("transactions/single/<products_id>/", transactions_views.TransactionsAPI.as_view()),

    #CURRENCIES
    path("currency-converter/", currencies_views.CurrencyConverterAPI.as_view(), name="currency-converter"),

    #REST
    path("categories/", views.CategoriesAPI.as_view(), name="categories"),

    path("brands/id/<int:id>/", views.BrandsAPI.as_view(), name="brands-by-id"),
    path("brands/category/<str:category>/", views.BrandsAPI.as_view(), name="brands-by-category"),
    path("recommendations/<id>/", views.Recommendations.as_view(), name="recommendations"),
    path("lobby-price-mod/<product_id>/<user_id>/", views.LobbyPriceMod.as_view(), name="lobby-price"),

    #PAYMENTS
    path("payment-creation/", payments_views.StripeCheckout.as_view(), name="payment"),
    path('stripe-webhook/', webhooks.WebhookTransaction.as_view(), name='stripe-webhook'),

]

