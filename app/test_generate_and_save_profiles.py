import os
import requests
import random
import pandas as pd
from dotenv import load_dotenv  # new

# ==========================
# 🔹 Load API key from .env
# ==========================
load_dotenv()  # loads variables from .env file in project root
API_KEY = os.getenv("QUANTSCORE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Please set QUANTSCORE_API_KEY in your .env file.")

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ==========================
# 🔹 API Endpoint
# ==========================
BASE_URL = "http://127.0.0.1:8000/predict"

# ==========================
# 🔹 Function to generate random credit profile
# ==========================
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

# ==========================
# 🔹 Generate and send profiles
# ==========================
results = []

for i in range(50):
    profile = generate_profile()
    response = requests.post(BASE_URL, json=profile, headers=HEADERS)

    if response.status_code == 200:
        output = response.json()
        combined = {**profile, **output}
        results.append(combined)
        print(f"Profile {i+1}: {output.get('risk_category', 'No category returned')}")
    else:
        print(f"Profile {i+1}: ERROR ({response.status_code})")

# ==========================
# 🔹 Save results to CSV
# ==========================
df = pd.DataFrame(results)
df.to_csv("simulated_credit_portfolio.csv", index=False)

print("\n✅ Saved results to simulated_credit_portfolio.csv")
