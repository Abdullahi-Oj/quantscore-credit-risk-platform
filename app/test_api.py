import requests
import json

# ==========================
# 🔹 API Endpoints
# ==========================
BASE_URL = "http://127.0.0.1:8000"
SINGLE_PREDICT = f"{BASE_URL}/predict"
BATCH_PREDICT = f"{BASE_URL}/batch_predict"

# ==========================
# 🔹 Sample Single Input
# ==========================
single_input = {
    "Age": 35,
    "MonthlyIncome": 250000,
    "LoanAmount": 800000,
    "LoanDuration": 12,
    "Dependents": 2,
    "CreditHistory": 1,
    "Gender": 1,
    "Married": 1,
    "Education": 1,
    "SelfEmployed": 0,
    "Savings": 500000,
    "TransactionsPerMonth": 15,
    "PreviousDefaults": 0,
    "RepaymentRatio": 0.8
}

# ==========================
# 🔹 Sample Batch Input
# ==========================
batch_input = [
    single_input,
    {
        "Age": 28,
        "MonthlyIncome": 150000,
        "LoanAmount": 500000,
        "LoanDuration": 24,
        "Dependents": 0,
        "CreditHistory": 1,
        "Gender": 0,
        "Married": 0,
        "Education": 1,
        "SelfEmployed": 1,
        "Savings": 200000,
        "TransactionsPerMonth": 10,
        "PreviousDefaults": 1,
        "RepaymentRatio": 0.5
    }
]

# ==========================
# 🔹 Function to Call Single Predict
# ==========================
def test_single_predict():
    response = requests.post(SINGLE_PREDICT, json=single_input)
    print("=== Single Predict ===")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
    else:
        print("Error:", response.status_code, response.text)

# ==========================
# 🔹 Function to Call Batch Predict
# ==========================
def test_batch_predict():
    response = requests.post(BATCH_PREDICT, json=batch_input)
    print("=== Batch Predict ===")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
    else:
        print("Error:", response.status_code, response.text)

# ==========================
# 🔹 Run Tests
# ==========================
if __name__ == "__main__":
    test_single_predict()
    test_batch_predict()
