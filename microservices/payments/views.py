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

            # Ensure all required fields are provided
            if not all([amount, description, item_name, quantity]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        url = 'https://api.paymongo.com/v1/checkout_sessions'
        secret_key = settings.PAYMONGO_SECRET_KEY
        encoded_secret_key = base64.b64encode(f"{secret_key}:".encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_secret_key}',
            'Content-Type': 'application/json',
        }

        # Prepare the data to send to PayMongo API
        checkout_data = {
            "data": {
                "attributes": {
                    "amount": amount,  # Amount is already in centavos
                    "description": description,
                    "currency": "PHP",
                    "line_items": [
                        {
                            "amount": amount,
                            "currency": "PHP",
                            "description": item_name,
                            "name": item_name,
                            "quantity": quantity
                        }
                    ],
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

# def create_checkout_session(request):
#     if request.method == 'POST':  # Ensure the method matches the API expectations
#         url = 'https://api.paymongo.com/v1/checkout_sessions'

#         # Extract and encode secret key
#         secret_key = settings.PAYMONGO_SECRET_KEY
#         encoded_secret_key = base64.b64encode(f"{secret_key}:".encode()).decode()

#         # Headers for the API request
#         headers = {
#             'Authorization': f'Basic {encoded_secret_key}',
#             'Content-Type': 'application/json',
#         }

#         # Checkout session data
#         data = {
#             "data": {
#                 "attributes": {
#                     "amount": 10000,  # Amount in centavos (10000 centavos = 100 PHP)
#                     "description": "Sample Payment",
#                     "currency": "PHP",
#                     "line_items": [
#                         {
#                             "amount": 10000,
#                             "currency": "PHP",
#                             "description": "Test Item",
#                             "name": "Sample Item",
#                             "quantity": 1
#                         }
#                     ],
#                     "redirect": {
#                         "success": "http://localhost:8000/payment/success",  # Success URL
#                         "failed": "http://localhost:8000/payment/failed"    # Failed URL
#                     }
#                 }
#             }
#         }

#         try:
#             # Logging for debugging
#             logger.debug(f"Request URL: {url}")
#             logger.debug(f"Request Headers: {headers}")
#             logger.debug(f"Request Data: {data}")

#             # POST request to PayMongo API
#             response = requests.post(url, headers=headers, json=data)
#             response.raise_for_status()  # Raises HTTPError for bad responses

#             # Logging response
#             logger.debug(f"Response Status Code: {response.status_code}")
#             logger.debug(f"Response Content: {response.text}")

#             # Check response and handle checkout session creation
#             if response.status_code == 201:
#                 checkout_url = response.json()['data']['attributes']['checkout_url']
#                 return JsonResponse({'checkout_url': checkout_url})
#             else:
#                 return JsonResponse({'error': 'Failed to create checkout session', 'details': response.text}, status=400)

#         except requests.exceptions.RequestException as e:
#             # Log and return error message
#             logger.error(f"Request Exception: {e}")
#             return JsonResponse({'error': str(e)}, status=500)

#     else:
#         return JsonResponse({'error': 'Invalid request method. Use POST instead of GET.'}, status=400)


