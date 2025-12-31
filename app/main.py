from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Optional, List
import os
import pandas as pd

from app.schemas import CreditData, PredictResponse, BatchPredictResponse
from app.utils.logger import get_logger
from app.utils.model_loader import ModelBundle

# ==========================
# 🔹 App Initialization
# ==========================
app = FastAPI(
    title="QuantScore Credit Scoring API",
    version="1.0"
)

logger = get_logger()
models = ModelBundle()

# ==========================
# 🔐 API KEY SECURITY
# ==========================
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    expected_key = os.getenv("QUANTSCORE_API_KEY")

    if not expected_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

# ==========================
# 🔹 Feature Mapping
# ==========================
feature_map = {
    "Age": "age",
    "MonthlyIncome": "income",
    "LoanAmount": "loan_amount",
    "LoanDuration": "loan_term_months",
    "Dependents": "dependents",
    "CreditHistory": "credit_history",
    "Gender": "gender",
    "Married": "married",
    "Education": "education",
    "SelfEmployed": "self_employed",
    "Savings": "savings",
    "TransactionsPerMonth": "transactions_per_month",
    "PreviousDefaults": "previous_defaults",
    "RepaymentRatio": "repayment_ratio"
}

def transform_input(data: dict):
    return {feature_map[k]: v for k, v in data.items()}

def engineer_features(df: pd.DataFrame):
    df["installment_per_month"] = df["loan_amount"] / df["loan_term_months"].replace(0, 1)
    df["installment_to_income"] = df["installment_per_month"] / df["income"].replace(0, 1)
    df["savings_to_loan"] = df["savings"] / (df["loan_amount"] + 1)
    df["debt_to_income"] = df["loan_amount"] / df["income"].replace(0, 1)
    return df

# ==========================
# 🔹 SECURED ENDPOINTS
# ==========================

@app.post("/predict", response_model=PredictResponse)
def predict(
    data: CreditData,
    api_key: str = Depends(verify_api_key)
):
    try:
        df = pd.DataFrame([transform_input(data.dict())])
        df = engineer_features(df)

        X = df[models.features]
        X_scaled = models.scaler.transform(X)

        raw_prob = models.model.predict_proba(X_scaled)[:, 1][0]
        prob = float(models.calibrator.predict([[raw_prob]])[0])

        risk = (
            "Low Risk" if prob < 0.35 else
            "Medium Risk" if prob < 0.65 else
            "High Risk"
        )

        logger.info(f"/predict | prob={prob:.2f} | risk={risk}")
        return PredictResponse(probability=prob, risk_category=risk)

    except Exception as e:
        logger.error(f"/predict ERROR | {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@app.post("/batch_predict", response_model=BatchPredictResponse)
def batch_predict(
    data: List[CreditData],
    api_key: str = Depends(verify_api_key)
):
    try:
        records = [transform_input(d.dict()) for d in data]
        df = pd.DataFrame(records)
        df = engineer_features(df)

        X = df[models.features]
        X_scaled = models.scaler.transform(X)

        probs = models.calibrator.predict(
            models.model.predict_proba(X_scaled)[:, 1].reshape(-1, 1)
        )

        results = [
            PredictResponse(
                probability=float(p),
                risk_category="Low Risk" if p < 0.35 else "Medium Risk" if p < 0.65 else "High Risk"
            )
            for p in probs
        ]

        return BatchPredictResponse(results=results)

    except Exception as e:
        logger.error(f"/batch_predict ERROR | {str(e)}")
        raise HTTPException(status_code=500, detail="Batch prediction failed")

# ==========================
# 🔹 SYSTEM ROUTES (OPTIONAL)
# ==========================

@app.get("/")
def root():
    return {"service": "QuantScore Credit Scoring API", "status": "running"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "version": models.version()
    }
