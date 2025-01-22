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

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data from the frontend
            incoming_data = json.loads(request.body)

            # PayMongo API endpoint
            paymongo_url = 'https://api.paymongo.com/v1/checkout_sessions'

            # Extract the required fields from the incoming payload
            payload = {
                "data": {
                    "attributes": {
                        "send_email_receipt": incoming_data.get("data", {}).get("attributes", {}).get("send_email_receipt", True),
                        "show_description": True,
                        "show_line_items": True,
                        "description": incoming_data.get("data", {}).get("attributes", {}).get("description", []),
                        "line_items": incoming_data.get("data", {}).get("attributes", {}).get("line_items", []),
                        "payment_method_types": incoming_data.get("data", {}).get("attributes", {}).get("payment_method_types", []),
                        "reference_number": incoming_data.get("data", {}).get("attributes", {}).get("reference_number", [])
                    }
                }
            }

            # Prepare the headers for the PayMongo API request
            headers = {
                'Authorization': 'Basic c2tfdGVzdF9MZlpSbnR5eG1aSmFoN2lhRmJZa2tmVGM6',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

            # Send the request to PayMongo API
            response = requests.post('https://api.paymongo.com/v1/checkout_sessions', headers=headers, json=payload)

            # Parse and return the response from PayMongo API
            if response.status_code == 201:
                # Successfully created a checkout session
                response_data = response.json()
                return JsonResponse({'checkout_url': response_data['data']['attributes']['checkout_url']}, status=201)
            else:
                # Handle errors from PayMongo API
                return JsonResponse({'error': 'Failed to create checkout session', 'details': response.json()}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)


# response -> post(detail.response) -> 

# post(req.data) -> finance.db (trinbox)

