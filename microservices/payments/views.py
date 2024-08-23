import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

class InitiatePaymentView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'usd')
        user_id = request.data.get('user_id')

        try:
            # Create a payment intent with Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses the smallest currency unit
                currency=currency,
                metadata={'user_id': user_id}
            )

            # Save the payment record in your database
            payment = Payment.objects.create(
                user_id=user_id,
                amount=amount,
                currency=currency,
                stripe_charge_id=intent['id'],
                status='pending'
            )

            return Response({
                'client_secret': intent['client_secret'],
                'payment_id': payment.id,
            })

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmPaymentView(APIView):
    def post(self, request):
        payment_id = request.data.get('payment_id')
        payment = Payment.objects.get(id=payment_id)

        try:
            # Retrieve the payment intent to confirm its status
            intent = stripe.PaymentIntent.retrieve(payment.stripe_charge_id)

            if intent.status == 'succeeded':
                payment.status = 'succeeded'
            else:
                payment.status = intent.status

            payment.save()

            return Response({'status': payment.status})

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
