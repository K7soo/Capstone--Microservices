import requests, base64, json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timezone

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
            response = requests.post(paymongo_url, headers=headers, json=payload)

            # Check the status code of the response
            if response.status_code == 201:
                response_data = response.json()

                # Extract the checkout session ID
                checkout_id = response_data['data']['id']
                checkout_url = response_data['data']['attributes']['checkout_url']

                # Call the function to send data to finance
                send_data_to_finance(checkout_id)

                # Return the checkout URL to the frontend
                return JsonResponse({'checkout_url': checkout_url['data']['attributes']['checkout_url']}, status=200)

            else:
                # Log the full error response for debugging
                print("PayMongo Error Response:", response.json())
                response_data = response.json()
                if response.status_code == 200:
                    checkout_id = response_data['data']['id']
                    send_data_to_finance(checkout_id)
                return JsonResponse({'error': 'Failed to create checkout session', 'details': response.json()}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            # Catch any other exceptions
            print("Unexpected Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=400)
   
@csrf_exempt
def send_data_to_finance(checkout_id):
    try:
        # Fetch the session details using the checkout_id
        session_url = f'https://api.paymongo.com/v1/checkout_sessions/{checkout_id}'
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{PAYMONGO_SECRET_KEY}:".encode()).decode()}',
            'Accept': 'application/json',
        }
        session_response = requests.get(session_url, headers=headers)

        if session_response.status_code == 200:
            session_data = session_response.json()
 
            # Extract the necessary data
            attributes = session_data['data']['attributes']
            total_amount = attributes['line_items'][0]['amount'] / 100  # Convert centavos to PHP
            created_at_timestamp = session_data['data']['attributes'].get('created_at', None)
            if created_at_timestamp:
                payment_date = datetime.fromtimestamp(created_at_timestamp, tz=timezone.utc).strftime('%Y-%m-%d')  # Extract and format the date
            else:
                payment_date = None

            # Prepare finance payload
            finance_payload = {
                "transaction_id": session_data['data']['id'],
                "PaymentDate": payment_date,
                "Amount": total_amount,
                "PaymentMethod": ', '.join(attributes['payment_method_types']),
                "Description": attributes['description']
            }

            # Send data to the finance system
            finance_url = "http://127.0.0.1:8005/payment-record/"  # Replace with your finance endpoint
            finance_response = requests.post(finance_url, json=finance_payload)

            if finance_response.status_code == 201:
                print("Data sent to finance system successfully")
            else:
                print("Failed to send data to finance:", finance_response.json())

        else:
            print("Failed to fetch session details:", session_response.json())

    except Exception as e:
        print("Error in send_data_to_finance:", str(e))


