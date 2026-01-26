# main.py – QuantScore Credit Scoring API (Production Ready)

from typing import Optional, List
import os

import pandas as pd
import shap
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.schemas import CreditData, CreditResponse
from app.utils.logger import get_logger
from app.utils.model_loader import ModelBundle


# =====================================================
# 🔹 APP INITIALIZATION
# =====================================================

app = FastAPI(
    title="QuantScore Credit Scoring API",
    version="1.2",
    description="AI-powered credit risk scoring API for African fintechs",
)

logger = get_logger()
models = ModelBundle()
explainer = shap.TreeExplainer(models.model)


# =====================================================
# 🔹 RATE LIMITER
# =====================================================

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


# =====================================================
# 🔐 API KEY SECURITY
# =====================================================


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    expected_key = os.getenv("QUANTSCORE_API_KEY")
    if not expected_key:
        logger.critical("API key missing from environment variables")
        raise HTTPException(status_code=500, detail="API key not configured")

    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# =====================================================
# 🔹 FEATURE ENGINEERING
# =====================================================

FEATURE_MAP = {
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
    "RepaymentRatio": "repayment_ratio",
}


def transform_input(data: dict) -> dict:
    return {FEATURE_MAP[k]: v for k, v in data.items()}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["installment_per_month"] = df["loan_amount"] / df["loan_term_months"].replace(0, 1)
    df["installment_to_income"] = df["installment_per_month"] / df["income"].replace(0, 1)
    df["savings_to_loan"] = df["savings"] / (df["loan_amount"] + 1)
    df["debt_to_income"] = df["loan_amount"] / df["income"].replace(0, 1)
    return df


# =====================================================
# 🧠 BUSINESS INTERPRETATION
# =====================================================


def interpret_result(probability: float) -> dict:
    if probability < 0.35:
        return {
            "risk_category": "APPROVE",
            "confidence": "High",
            "reason": (
                "Low predicted default risk based on income stability "
                "and repayment behavior."
            ),
        }

    if probability < 0.65:
        return {
            "risk_category": "REVIEW",
            "confidence": "Medium",
            "reason": "Moderate risk detected. Manual review recommended.",
        }

    return {
        "risk_category": "REJECT",
        "confidence": "High",
        "reason": (
            "High default risk driven by income, repayment ratio, "
            "and credit history."
        ),
    }


# =====================================================
# 🔹 PREDICT ENDPOINT
# =====================================================

@app.post("/predict", response_model=CreditResponse)
@limiter.limit("100/minute")
def predict(
    request: Request, data: CreditData, api_key: str = Depends(verify_api_key)
):
    try:
        df = pd.DataFrame([transform_input(data.dict())])
        df = engineer_features(df)
        X_scaled = models.scaler.transform(df[models.features])
        raw_prob = models.model.predict_proba(X_scaled)[:, 1][0]
        calibrated_prob = float(models.calibrator.predict([[raw_prob]])[0])
        interp = interpret_result(calibrated_prob)

        return CreditResponse(
            probability=round(calibrated_prob, 4),
            risk_category=interp["risk_category"],
            confidence=interp["confidence"],
            reason=interp["reason"],
        )

    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed")


# =====================================================
# 🔹 EXPLAIN ENDPOINT
# =====================================================

@app.post("/explain", response_model=CreditResponse)
@limiter.limit("50/minute")
def explain(
    request: Request, data: CreditData, api_key: str = Depends(verify_api_key)
):
    try:
        df = pd.DataFrame([transform_input(data.dict())])
        df = engineer_features(df)
        X_scaled = models.scaler.transform(df[models.features])
        raw_prob = models.model.predict_proba(X_scaled)[0][1]
        calibrated_prob = float(models.calibrator.predict([[raw_prob]])[0])
        interp = interpret_result(calibrated_prob)

        return CreditResponse(
            probability=round(calibrated_prob, 4),
            risk_category=interp["risk_category"],
            confidence=interp["confidence"],
            reason=interp["reason"],
        )

    except Exception:
        logger.exception("Explain failed")
        raise HTTPException(status_code=500, detail="Explain failed")


# =====================================================
# 🔹 BATCH PREDICT ENDPOINT
# =====================================================

@app.post("/batch_predict", response_model=List[CreditResponse])
@limiter.limit("30/minute")
def batch_predict(
    request: Request, data: List[CreditData], api_key: str = Depends(verify_api_key)
):
    try:
        df = pd.DataFrame([transform_input(d.dict()) for d in data])
        df = engineer_features(df)
        X_scaled = models.scaler.transform(df[models.features])
        raw_probs = models.model.predict_proba(X_scaled)[:, 1]
        probs = models.calibrator.predict(raw_probs.reshape(-1, 1))

        results = [
            CreditResponse(
                probability=round(float(p), 4),
                risk_category=interpret_result(p)["risk_category"],
                confidence=interpret_result(p)["confidence"],
                reason=interpret_result(p)["reason"],
            )
            for p in probs
        ]

        return results

    except Exception:
        logger.exception("Batch prediction failed")
        raise HTTPException(status_code=500, detail="Batch prediction failed")


# =====================================================
# 🔹 SYSTEM ROUTES
# =====================================================

@app.get("/")
def root():
    return {"service": "QuantScore Credit Scoring API", "status": "running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "model_version": models.version(),
    }
