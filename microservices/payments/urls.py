from django.urls import path
from .views import InitiatePaymentView, ConfirmPaymentView

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('confirm/', ConfirmPaymentView.as_view(), name='confirm_payment'),
]
