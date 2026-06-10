import sys
sys.path.insert(0, ".")

from app.ml.preprocessing import transform_input, engineer_features
import pandas as pd

payload = {
    "Age": 30,
    "MonthlyIncome": 250000,
    "LoanAmount": 800000,
    "LoanDuration": 12,
    "Dependents": 0,
    "CreditHistory": 1,
    "Gender": 1,
    "Married": 0,
    "Education": 1,
    "SelfEmployed": 0,
    "Savings": 500000,
    "TransactionsPerMonth": 10,
    "PreviousDefaults": 0,
    "RepaymentRatio": 0.8,
}

transformed = transform_input(payload)
df = pd.DataFrame([transformed])
df = engineer_features(df)

print("Columns produced:", df.columns.tolist())
print("Count:", len(df.columns))