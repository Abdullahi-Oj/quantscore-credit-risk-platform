import requests
import random
import pandas as pd

BASE_URL = "http://127.0.0.1:8000/predict"
API_KEY = "qs_2025_secure_key_123"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def generate_profile():
    return {
        "Age": random.randint(21, 65),
        "CreditHistory": random.choice([0, 1]),
        "Dependents": random.randint(0, 5),
        "Education": random.choice([0, 1]),
        "Gender": random.choice([0, 1]),
        "LoanAmount": random.randint(50_000, 2_000_000),
        "LoanDuration": random.choice([6, 12, 24, 36]),
        "Married": random.choice([0, 1]),
        "MonthlyIncome": random.randint(80_000, 1_200_000),
        "PreviousDefaults": random.randint(0, 3),
        "RepaymentRatio": round(random.uniform(0.2, 0.95), 2),
        "Savings": random.randint(0, 2_500_000),
        "SelfEmployed": random.choice([0, 1]),
        "TransactionsPerMonth": random.randint(0, 60)
    }

results = []

for i in range(50):
    profile = generate_profile()
    response = requests.post(BASE_URL, json=profile, headers=HEADERS)

    if response.status_code == 200:
        output = response.json()
        combined = {**profile, **output}
        results.append(combined)
        print(f"Profile {i+1}: {output['risk_category']}")
    else:
        print(f"Profile {i+1}: ERROR")

df = pd.DataFrame(results)
df.to_csv("simulated_credit_portfolio.csv", index=False)

print("\n✅ Saved results to simulated_credit_portfolio.csv")
