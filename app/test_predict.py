import os
import requests
import json
from dotenv import load_dotenv  # for loading .env file

# ==========================
# 🔹 Load API key from .env
# ==========================
load_dotenv()  # looks for .env file in project root
API_KEY = os.getenv("QUANTSCORE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Please set QUANTSCORE_API_KEY in your .env file.")

# ==========================
# 🔹 API endpoint
# ==========================
BASE_URL = "http://127.0.0.1:8000"
SINGLE_PREDICT = f"{BASE_URL}/predict"

# ==========================
# 🔹 Input data
# ==========================
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

# ==========================
# 🔹 API headers
# ==========================
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ==========================
# 🔹 Send request
# ==========================
response = requests.post(SINGLE_PREDICT, json=single_input, headers=headers)

# ==========================
# 🔹 Print response
# ==========================
if response.status_code == 200:
    print("Prediction Response:")
    print(json.dumps(response.json(), indent=4))
else:
    print("Error:", response.status_code, response.text)
