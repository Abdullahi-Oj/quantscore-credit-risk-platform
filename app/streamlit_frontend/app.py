# streamlit_frontend/app.py

import streamlit as st
import requests
import os

# ==========================
# 🔹 App Config
# ==========================
st.set_page_config(
    page_title="QuantScore Credit Risk Assessment",
    page_icon="📊",
    layout="centered"
)

API_URL = os.getenv("QUANTSCORE_API_URL", "http://127.0.0.1:8000/explain")
API_KEY = os.getenv("QUANTSCORE_API_KEY")

# ==========================
# 🔹 App Title
# ==========================
st.title("📊 QuantScore Credit Risk Assessment")
st.write("Enter customer details to evaluate loan default risk.")

# ==========================
# 🔹 Input Form
# ==========================
with st.form("credit_form"):
    Age = st.number_input("Age", min_value=18, max_value=75, value=30)
    MonthlyIncome = st.number_input("Monthly Income (₦)", min_value=0.0, value=250000.0)
    LoanAmount = st.number_input("Loan Amount (₦)", min_value=0.0, value=800000.0)
    LoanDuration = st.number_input("Loan Duration (Months)", min_value=1, value=12)

    Dependents = st.number_input("Number of Dependents", min_value=0, value=0)
    CreditHistory = st.selectbox("Credit History", [0, 1])
    Gender = st.selectbox("Gender", [0, 1])
    Married = st.selectbox("Marital Status", [0, 1])
    Education = st.selectbox("Education Level", [0, 1])
    SelfEmployed = st.selectbox("Self Employed", [0, 1])

    Savings = st.number_input("Savings (₦)", min_value=0.0, value=500000.0)
    TransactionsPerMonth = st.number_input("Transactions per Month", min_value=0, value=10)
    PreviousDefaults = st.selectbox("Previous Defaults", [0, 1])
    RepaymentRatio = st.slider("Repayment Ratio", 0.0, 1.0, 0.8)

    submitted = st.form_submit_button("🔍 Score Credit Risk")

# ==========================
# 🔹 Submit Logic
# ==========================
if submitted:
    if not API_KEY:
        st.error("API key not configured. Set QUANTSCORE_API_KEY environment variable.")
    else:
        payload = {
            "Age": Age,
            "MonthlyIncome": MonthlyIncome,
            "LoanAmount": LoanAmount,
            "LoanDuration": LoanDuration,
            "Dependents": Dependents,
            "CreditHistory": CreditHistory,
            "Gender": Gender,
            "Married": Married,
            "Education": Education,
            "SelfEmployed": SelfEmployed,
            "Savings": Savings,
            "TransactionsPerMonth": TransactionsPerMonth,
            "PreviousDefaults": PreviousDefaults,
            "RepaymentRatio": RepaymentRatio
        }

        headers = {"x-api-key": API_KEY}

        with st.spinner("Scoring credit risk..."):
            try:
                res = requests.post(API_URL, json=payload, headers=headers)
                if res.status_code == 200:
                    result = res.json()
                    st.success("Assessment Completed ✅")
                    st.metric("Default Probability", f"{result['probability']:.2%}")
                    st.info(f"Decision: {result['risk_category']}")
                    st.write(f"Confidence: {result['confidence']}")
                    st.write(result["reason"])
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
