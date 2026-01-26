import os
import requests
import json
from dotenv import load_dotenv  # for loading API key from .env

# ==========================
# 🔹 Load API key from .env
# ==========================
load_dotenv()  # loads variables from .env in project root
API_KEY = os.getenv("QUANTSCORE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Please set QUANTSCORE_API_KEY in your .env file.")

# ==========================
# 🔹 Config
# ==========================
BASE_URL = "http://127.0.0.1:8000"

headers = {
    "accept": "application/json",
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ==========================
# 🔹 Sample inputs
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

batch_input = [single_input, single_input]  # example batch

# ==========================
# 🔹 Helper function to send POST requests
# ==========================
def post_request(endpoint, data):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"\n✅ Response from /{endpoint}:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"\n❌ Error {response.status_code} from /{endpoint}: {response.text}")

# ==========================
# 🔹 Test endpoints
# ==========================
post_request("predict", single_input)
post_request("explain", single_input)
post_request("batch_predict", batch_input)
