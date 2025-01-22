import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import base64
import json

# Views for homepage and payment success/failure
def home(request):
    return render(request, 'index.html')


PAYMONGO_SECRET_KEY = "sk_test_LfZRntyxmZJah7iaFbYkkfTc"
PAYMONGO_URL = "https://api.paymongo.com/v1/checkout_sessions"


def create_checkout_session(request):
    if request.method == 'POST':
        # Parse data
        data = json.loads(request.body)
        amount = data.get('amount')
        description = data.get('description')
        name = data.get('name')
        quantity = data.get('quantity')
        reference_number = data.get('reference_number')

        # Prepare PayMongo API request
        url = "https://api.paymongo.com/v1/checkout_sessions"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "authorization": "Basic YOUR_SECRET_KEY_BASE64_ENCODED"
        }
        payload = {
            "data": {
                "attributes": {
                    "send_email_receipt": False,
                    "show_description": True,
                    "show_line_items": True,
                    "description": description,
                    "line_items": [
                        {
                            "currency": "PHP",
                            "amount": amount,
                            "description": description,
                            "name": name,
                            "quantity": quantity,
                        }
                    ],
                    "payment_method_types": ["gcash"],
                    "reference_number": reference_number
                }
            }
        }

        # Make the API call to PayMongo
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            checkout_url = response.json().get('data').get('attributes').get('checkout_url')
            return JsonResponse({'checkout_url': checkout_url})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)



