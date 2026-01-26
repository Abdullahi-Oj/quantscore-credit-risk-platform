import os
import requests
import json
import random
from dotenv import load_dotenv  # load .env file

# ==========================
# 🔹 Load API key from .env
# ==========================
load_dotenv()  # loads QUANTSCORE_API_KEY from .env
API_KEY = os.getenv("QUANTSCORE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Please set QUANTSCORE_API_KEY in your .env file.")

# ==========================
# 🔹 API endpoint
# ==========================
BASE_URL = "http://127.0.0.1:8000"
SINGLE_PREDICT = f"{BASE_URL}/predict"

# ==========================
# 🔹 Function to generate a realistic random profile
# ==========================
def generate_profile():
    return {
        "Age": random.randint(18, 65),
        "CreditHistory": random.choice([0, 1]),
        "Dependents": random.randint(0, 5),
        "Education": random.choice([0, 1]),
        "Gender": random.choice([0, 1]),
        "LoanAmount": random.randint(50000, 2000000),
        "LoanDuration": random.choice([6, 12, 24, 36]),
        "Married": random.choice([0, 1]),
        "MonthlyIncome": random.randint(50000, 1000000),
        "PreviousDefaults": random.randint(0, 3),
        "RepaymentRatio": round(random.uniform(0.2, 1.0), 2),
        "Savings": random.randint(0, 2000000),
        "SelfEmployed": random.choice([0, 1]),
        "TransactionsPerMonth": random.randint(0, 50)
    }

# ==========================
# 🔹 Generate 10 random profiles
# ==========================
profiles = [generate_profile() for _ in range(10)]

# ==========================
# 🔹 Send each profile to /predict
# ==========================
for idx, profile in enumerate(profiles, start=1):
    response = requests.post(
        SINGLE_PREDICT,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=profile
    )

    print(f"\nProfile #{idx} Input:")
    print(json.dumps(profile, indent=4))
    
    if response.status_code == 200:
        print("Prediction Response:")
        print(json.dumps(response.json(), indent=4))
    else:
        print("Error:", response.status_code, response.text)
