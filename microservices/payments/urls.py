from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
]
