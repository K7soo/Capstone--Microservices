from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('payment/success/', views.payment_success, name='payment-success'),
    path('payment/failed/', views.payment_failed, name='payment-failed'),
]
