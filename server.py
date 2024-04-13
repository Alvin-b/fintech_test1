from flask import Flask, request, jsonify, render_template
import hashlib
import requests
import datetime
import secrets
import base64

app = Flask(__name__)

# Daraja API constants
DARAJA_BASE_URL = "https://sandbox.safaricom.co.ke/"
DARAJA_CONSUMER_KEY = "YW53gKgl1LTfV8t82kef87bvmmck2azoL9KhD6BQg8AahQWB"
DARAJA_CONSUMER_SECRET = "wfw137EkDh95AAACKmIKv3GNsLGZdshQiA8awUJo6GHVuNlXawgLHHYXpgIgqGwq"
SHORTCODE = "174379"  # Your Paybill or Buy Goods Till number
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

# Secret key for hashing algorithm
SECRET_KEY = secrets.token_hex(16)

# Function to generate a hash code using SHA-256 algorithm
def generate_hash(data):
    hash_object = hashlib.sha256(SECRET_KEY.encode() + data.encode())
    return hash_object.hexdigest()

# Function to obtain access token from Daraja API
def get_access_token():
    url = DARAJA_BASE_URL + "oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(DARAJA_CONSUMER_KEY, DARAJA_CONSUMER_SECRET))
    data = response.json()
    return data.get("access_token")

# Route to receive payment details and process payment
@app.route("/process_payment", methods=["POST"])
def process_payment():
    # Get payment details from the request
    payment_data = request.get_json()
    amount = payment_data.get("amount")
    phone_number = payment_data.get("phone_number")

    if not amount or not phone_number:
        return jsonify({"success": False, "message": "Amount and phone number are required."}), 400

    # Call Daraja API to process payment
    access_token = get_access_token()
    if access_token:
        url = DARAJA_BASE_URL + "mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode('utf-8')

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://mydomain.com/path",
            "AccountReference": "test",
            "TransactionDesc": "Test Payment"
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            # Payment processing successful
            return render_template("payment_successful.html")
        else:
            # Payment processing failed
            return render_template("payment_failed.html")
    else:
        # Failed to obtain access token
        return jsonify({"success": False, "message": "Failed to obtain access token."}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000) #my public ip address
