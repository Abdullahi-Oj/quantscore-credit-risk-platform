"""
Streamlit demo frontend for QuantScore API.

This UI is for demonstration and internal testing only.
Core credit risk logic, validation, and scoring
live in the backend service.
"""

import os

import requests
import streamlit as st

# ==========================
# 🔹 App Config
# ==========================
st.set_page_config(
    page_title="QuantScore Credit Risk Assessment",
    page_icon="📊",
    layout="centered",
)

API_URL = os.getenv(
    "QUANTSCORE_API_URL",
    "http://127.0.0.1:8000/predict",
)
API_KEY = os.getenv("QUANTSCORE_API_KEY", "")

# ==========================
# 🔹 App Title
# ==========================
st.title("📊 QuantScore Credit Risk Assessment")
st.write(
    "Enter customer financial details to evaluate loan default risk "
    "using a calibrated machine learning model."
)

# ==========================
# 🔹 Input Form (UI-Friendly)
# ==========================
with st.form("credit_form"):
    age = st.number_input(
        "Age",
        min_value=18,
        max_value=75,
        value=30,
    )

    monthly_income = st.number_input(
        "Monthly Income (₦)",
        min_value=0.0,
        value=250_000.0,
    )

    loan_amount = st.number_input(
        "Loan Amount (₦)",
        min_value=0.0,
        value=800_000.0,
    )

    loan_duration = st.number_input(
        "Loan Duration (Months)",
        min_value=1,
        value=12,
    )

    savings = st.number_input(
        "Savings (₦)",
        min_value=0.0,
        value=500_000.0,
    )

    transactions_per_month = st.number_input(
        "Transactions per Month",
        min_value=0,
        value=10,
    )

    previous_defaults = st.selectbox(
        "Previous Loan Defaults",
        [0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No",
    )

    repayment_ratio = st.slider(
        "Repayment Ratio (Installment ÷ Income)",
        0.0,
        1.0,
        0.8,
    )

    submitted = st.form_submit_button("🔍 Score Credit Risk")

# ==========================
# 🔹 Submit Logic
# ==========================
if submitted:
    if not API_KEY:
        st.error(
            "API key not configured. "
            "Set the QUANTSCORE_API_KEY environment variable."
        )
    else:
        # --------------------------------------------------
        # 🔹 MODEL-ALIGNED PAYLOAD (snake_case, exact features)
        # --------------------------------------------------
        payload = {
            "age": age,
            "income": monthly_income,
            "loan_amount": loan_amount,
            "loan_term_months": loan_duration,
            "savings": savings,
            "transactions_per_month": transactions_per_month,
            "previous_defaults": previous_defaults,
            "repayment_ratio": repayment_ratio,
        }

        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        }

        with st.spinner("Scoring credit risk..."):
            try:
                response = requests.post(
                    API_URL,
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except ValueError:
                        st.error(
                            "Invalid response format received from API."
                        )
                        st.stop()

                    st.success("Assessment Completed ✅")

                    st.metric(
                        "Default Probability",
                        f"{result['probability']:.2%}",
                    )

                    st.info(
                        f"Risk Category: {result['risk_category']}"
                    )

                    if "confidence" in result:
                        st.write(
                            f"Model Confidence: {result['confidence']}"
                        )

                    if "reason" in result:
                        st.write("🧠 Model Insight")
                        st.write(result["reason"])

                else:
                    st.error(
                        f"API Error ({response.status_code}): "
                        f"{response.text}"
                    )

            except requests.exceptions.RequestException as exc:
                st.error(f"Connection error: {exc}")
