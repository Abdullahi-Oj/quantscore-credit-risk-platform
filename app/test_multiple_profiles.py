import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000"
SINGLE_PREDICT = f"{BASE_URL}/predict"
API_KEY = "qs_2025_secure_key_123"

# Function to generate a realistic random profile
def generate_profile():
    profile = {
        "Age": random.randint(18, 65),  # realistic adult age
        "CreditHistory": random.choice([0, 1]),  # 0 = bad, 1 = good
        "Dependents": random.randint(0, 5),
        "Education": random.choice([0, 1]),  # 0 = no degree, 1 = degree
        "Gender": random.choice([0, 1]),  # 0 = female, 1 = male
        "LoanAmount": random.randint(50000, 2000000),  # in Naira
        "LoanDuration": random.choice([6, 12, 24, 36]),  # months
        "Married": random.choice([0, 1]),
        "MonthlyIncome": random.randint(50000, 1000000),
        "PreviousDefaults": random.randint(0, 3),
        "RepaymentRatio": round(random.uniform(0.2, 1.0), 2),  # portion of income
        "Savings": random.randint(0, 2000000),
        "SelfEmployed": random.choice([0, 1]),
        "TransactionsPerMonth": random.randint(0, 50)
    }
    return profile

# Generate 10 profiles
profiles = [generate_profile() for _ in range(10)]

# Send each profile to /predict
for idx, profile in enumerate(profiles, start=1):
    response = requests.post(
        SINGLE_PREDICT,
        headers={"x-api-key": API_KEY},
        json=profile
    )

    print(f"\nProfile #{idx} Input:")
    print(json.dumps(profile, indent=4))
    
    if response.status_code == 200:
        print("Prediction Response:")
        print(json.dumps(response.json(), indent=4))
    else:
        print("Error:", response.status_code, response.text)
