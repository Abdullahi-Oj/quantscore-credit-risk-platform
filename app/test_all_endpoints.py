import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("QUANTSCORE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Set QUANTSCORE_API_KEY in .env")

BASE_URL = "http://127.0.0.1:8000"
headers  = {
    "accept":       "application/json",
    "x-api-key":    API_KEY,
    "Content-Type": "application/json",
}


def post(endpoint, data):
    r = requests.post(f"{BASE_URL}/{endpoint}", headers=headers, json=data)
    if r.status_code == 200:
        print(f"\n✅ /{endpoint}:")
        print(json.dumps(r.json(), indent=4))
    else:
        print(f"\n❌ Error {r.status_code} from /{endpoint}: {r.text}")


def get(endpoint):
    r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)
    if r.status_code == 200:
        print(f"\n✅ /{endpoint}:")
        print(json.dumps(r.json(), indent=4))
    else:
        print(f"\n❌ Error {r.status_code} from /{endpoint}: {r.text}")


# ── Applicant profiles ────────────────────────────────────────

# Very high risk — high debt, low income, no savings
high_risk = {
    "Age": 45,
    "MonthlyIncome": 80000,
    "LoanAmount": 1200000,
    "LoanDuration": 24,
    "Dependents": 4,
    "CreditHistory": 0,
    "Gender": 1,
    "Married": 0,
    "Education": 0,
    "SelfEmployed": 1,
    "Savings": 10000,
    "TransactionsPerMonth": 3,
    "PreviousDefaults": 3,
    "RepaymentRatio": 0.2,
}

# Adjusted medium risk — DTI just above 1.0, borderline profile
medium_risk = {
    "Age": 35,
    "MonthlyIncome": 300000,
    "LoanAmount": 450000,      # DTI = 1.5 — sits in medium zone
    "LoanDuration": 18,
    "Dependents": 2,
    "CreditHistory": 1,
    "Gender": 1,
    "Married": 1,
    "Education": 1,
    "SelfEmployed": 0,
    "Savings": 40000,
    "TransactionsPerMonth": 8,
    "PreviousDefaults": 1,
    "RepaymentRatio": 0.5,
}
# Low risk — low debt, high income, strong savings
low_risk = {
    "Age": 40,
    "MonthlyIncome": 2000000,
    "LoanAmount": 200000,
    "LoanDuration": 12,
    "Dependents": 0,
    "CreditHistory": 1,
    "Gender": 1,
    "Married": 1,
    "Education": 1,
    "SelfEmployed": 0,
    "Savings": 5000000,
    "TransactionsPerMonth": 25,
    "PreviousDefaults": 0,
    "RepaymentRatio": 0.95,
}

# ── Tests ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PROFILE TESTS — expecting different probabilities")
print("=" * 60)

print("\n--- HIGH RISK applicant ---")
post("predict", high_risk)

print("\n--- MEDIUM RISK applicant ---")
post("predict", medium_risk)

print("\n--- LOW RISK applicant ---")
post("predict", low_risk)

print("\n--- EXPLAIN (low risk applicant) ---")
post("explain", low_risk)

print("\n--- BATCH (high + low risk) ---")
post("batch_predict", {"applicants": [high_risk, low_risk]})

print("\n" + "=" * 60)
print("OTHER ENDPOINTS")
print("=" * 60)

get("feature-importance")

print("\n" + "=" * 60)