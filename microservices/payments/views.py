import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import base64
import json
from datetime import datetime

# Views for homepage and payment success/failure
def home(request):
    return render(request, 'index.html')

def success(request):
    return render(request, 'payment_success.html')


PAYMONGO_SECRET_KEY = "sk_test_LfZRntyxmZJah7iaFbYkkfTc"
PAYMONGO_URL = "https://api.paymongo.com/v1/checkout_sessions"

import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def create_checkout_session(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data from the frontend
            incoming_data = json.loads(request.body)

            # PayMongo API endpoint
            checkout_url = 'https://api.paymongo.com/v1/checkout_sessions'

            # Extract the required fields from the incoming payload
            payload = {
                "data": {
                    "attributes": {
                        "send_email_receipt": incoming_data.get("data", {}).get("attributes", {}).get("send_email_receipt", True),
                        "show_description": True,
                        "show_line_items": True,
                        "description": incoming_data.get("data", {}).get("attributes", {}).get("description", []),
                        "success_url": incoming_data.get("data", {}).get("attributes", {}).get("success_url", []),
                        "line_items": incoming_data.get("data", {}).get("attributes", {}).get("line_items", []),
                        "payment_method_types": incoming_data.get("data", {}).get("attributes", {}).get("payment_method_types", []),
                        "reference_number": incoming_data.get("data", {}).get("attributes", {}).get("reference_number", [])
                    }
                }
            }

            # Prepare the headers for the PayMongo API request
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{PAYMONGO_SECRET_KEY}:".encode()).decode()}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

            # Send the request to PayMongo API
            response = requests.post(checkout_url, headers=headers, json=payload)

            # Check the status code of the response
            if response.status_code == 201:
                response_data = response.json()

                # Extract the checkout URL
                checkout_url = response_data['data']['attributes'].get('checkout_url')
                    # Send data to the finance system
                send_data_to_finance(response_data)

                    # Return the checkout URL to the frontend
                return JsonResponse({'checkout_url': checkout_url}, status=201)

            else:
                # Log the full error response for debugging
                print("PayMongo Error Response:", response.json())
                return JsonResponse({'error': 'Failed to create checkout session', 'details': response.json()}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            # Catch any other exceptions
            print("Unexpected Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)
   
    
def send_data_to_finance(response_data):
    try:
        # Extract the total amount
        line_items = response_data['data']['attributes'].get('line_items', [])
        total_amount = sum(item.get('amount', 0) for item in line_items)

        # Fallback to payment_intent if line_items are missing or zero
        if total_amount == 0:
            total_amount = response_data['data']['attributes']['payment_intent']['attributes'].get('amount', 0)

        # Convert `created_at` to ISO 8601 format
        created_at_timestamp = response_data['data']['attributes'].get('created_at', None)
        if created_at_timestamp:
            payment_date = datetime.utcfromtimestamp(created_at_timestamp).isoformat() + "Z"  # Add 'Z' for UTC time
        else:
            payment_date = None  # Handle missing timestamp appropriately

        # Prepare the finance payload
        finance_payload = {
            "transaction_id": response_data['data']['id'],
            "PaymentDate": payment_date,
            "Amount": total_amount / 100,  # Convert centavos to PHP
            "PaymentMethod": ', '.join(response_data['data']['attributes']['payment_method_types']),
            "Description": response_data['data']['attributes']['description']
        }

        # Send data to the finance system
        finance_url = "http://127.0.0.1:8000w/payment-record/"  # Replace with your finance endpoint
        finance_response = requests.post(finance_url, json=finance_payload)

        if finance_response.status_code == 201:
            print("Data sent to finance system successfully")
        else:
            print("Failed to send data to finance:", finance_response.json())
    except KeyError as e:
        print(f"Error extracting or sending data to finance system: {e}")
    except Exception as e:
        print(f"Error sending data to finance system: {e}")
    