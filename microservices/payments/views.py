import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import logging
import base64

def home(request):
    return HttpResponse("Welcome to the home page!")

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')


logger = logging.getLogger(__name__)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        url = 'https://api.paymongo.com/v1/checkout_sessions'

        secret_key = settings.PAYMONGO_SECRET_KEY
        encoded_secret_key = base64.b64encode(f"{secret_key}:".encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_secret_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            "data": {
                "attributes": {
                    "amount": 10000,  # Amount in centavos (10000 centavos = 100 PHP)
                    "description": "Sample Payment",
                    "currency": "PHP",
                    "line_items": [
                        {
                            "amount": 10000,
                            "currency": "PHP",
                            "description": "Test Item",
                            "name": "Sample Item",
                            "quantity": 1
                        }
                    ],
                    "redirect": {
                        "success": "http://localhost:8000/payment/success",  # Redirect URL after successful payment
                        "failed": "http://localhost:8000/payment/failed"    # Redirect URL after failed payment
                    }
                }
            }
        }
        
        try:
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request Headers: {headers}")
            logger.debug(f"Request Data: {data}")

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raises HTTPError for bad responses

            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Content: {response.text}")
            print('try test')

            if response.status_code == 201:
                checkout_url = response.json()['data']['attributes']['checkout_url']
                print('if else clause 1')
                return JsonResponse({'checkout_url': checkout_url})
            else:
                print('if else clause 2')
                return JsonResponse({'error': 'Failed to create checkout session', 'details': response.text}, status=400)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Exception: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        print('if else clause 3')
        return JsonResponse({'error': 'Invalid request method'}, status=400)


