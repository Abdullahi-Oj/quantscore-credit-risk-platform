import requests
import json

# --- Config ---
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "qs_2025_secure_key_123"  # your API key

headers = {
    "accept": "application/json",
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# --- Sample single input ---
single_input = {
    "Age": 30,
    "CreditHistory": 1,
    "Dependents": 0,
    "Education": 1,
    "Gender": 1,
    "LoanAmount": 800000,
    "LoanDuration": 12,
    "Married": 0,
    "MonthlyIncome": 250000,
    "PreviousDefaults": 0,
    "RepaymentRatio": 0.8,
    "Savings": 500000,
    "SelfEmployed": 0,
    "TransactionsPerMonth": 10
}

# --- Batch input (list of records) ---
batch_input = [single_input, single_input]  # example: two identical records

# --- Helper function to send POST requests ---
def post_request(endpoint, data):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"\n✅ Response from /{endpoint}:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"\n❌ Error {response.status_code} from /{endpoint}: {response.text}")

# --- Test /predict ---
post_request("predict", single_input)

# --- Test /explain ---
post_request("explain", single_input)

# --- Test /batch_predict ---
post_request("batch_predict", batch_input)
