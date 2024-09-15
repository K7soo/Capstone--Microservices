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

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')

logger = logging.getLogger(__name__)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        # Parse JSON data from the request
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            description = data.get('description')
            item_name = data.get('item_name')
            quantity = data.get('quantity')
            customer_name = data.get('name')  # Assuming 'name' is sent from the frontend
            customer_email = data.get('email')  # Assuming 'email' is sent from the frontend

            # Ensure all required fields are provided
            if not all([amount, description, item_name, quantity, customer_name, customer_email]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        url = settings.URL
        secret_key = settings.PAYMONGO_SECRET_KEY
        encoded_secret_key = base64.b64encode(f"{secret_key}:".encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_secret_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Prepare the data to send to PayMongo API following the format you provided
        checkout_data = {
            "data": {
                "attributes": {
                    "billing": {
                        "name": customer_name,
                        "email": customer_email
                    },
                    "send_email_receipt": False,
                    "show_description": False,
                    "show_line_items": True,
                    "line_items": [
                        {
                            "currency": "PHP",
                            "amount": amount,  # Amount should be in centavos
                            "name": item_name,
                            "quantity": quantity
                        }
                    ],
                    "payment_method_types": ["gcash"],  # Assuming gcash for now
                    "reference_number": "TR-001",  # Sample reference number
                    "redirect": {
                        "success": "http://localhost:8000/payment/success",  # Success URL
                        "failed": "http://localhost:8000/payment/failed"    # Failed URL
                    }
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=checkout_data)
            response.raise_for_status()

            if response.status_code == 201:
                checkout_url = response.json()['data']['attributes']['checkout_url']
                return JsonResponse({'checkout_url': checkout_url})
            else:
                return JsonResponse({'error': 'Failed to create checkout session', 'details': response.text}, status=400)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request Exception: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method. Use POST instead of GET.'}, status=400)


