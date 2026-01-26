import requests
import json

# API endpoint
BASE_URL = "http://127.0.0.1:8000"
SINGLE_PREDICT = f"{BASE_URL}/predict"

# Input data
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

# API Key header
headers = {"x-api-key": "qs_2025_secure_key_123"}

# Send request
response = requests.post(SINGLE_PREDICT, json=single_input, headers=headers)

# Print response
if response.status_code == 200:
    print("Prediction Response:")
    print(json.dumps(response.json(), indent=4))
else:
    print("Error:", response.status_code, response.text)
