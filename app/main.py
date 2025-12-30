from fastapi import FastAPI, HTTPException
import pandas as pd
from app.schemas import CreditData, PredictResponse, BatchPredictResponse
from app.utils.logger import get_logger
from app.utils.model_loader import ModelBundle

# ==========================
# 🔹 App
# ==========================
app = FastAPI(
    title="QuantScore Credit Scoring API",
    version="1.0"
)

logger = get_logger()
models = ModelBundle()

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
    # Avoid division by zero by replacing 0 with 1 temporarily
    df["installment_per_month"] = df["loan_amount"] / df["loan_term_months"].replace(0, 1)
    df["installment_to_income"] = df["installment_per_month"] / df["income"].replace(0, 1)
    df["savings_to_loan"] = df["savings"] / (df["loan_amount"] + 1)  # +1 to avoid zero division
    df["debt_to_income"] = df["loan_amount"] / df["income"].replace(0, 1)
    return df



# ==========================
# 🔹 Endpoints
# ==========================
@app.post("/predict", response_model=PredictResponse)
def predict(data: CreditData):
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
def batch_predict(data: list[CreditData]):
    try:
        # Convert all incoming records into a DataFrame
        records = [transform_input(d.dict()) for d in data]
        df = pd.DataFrame(records)

        # Engineer features safely (already handles zero-division)
        df = engineer_features(df)

        # Ensure all model features exist in the DataFrame
        for col in models.features:
            if col not in df.columns:
                df[col] = 0

        # Extract features and scale
        X = df[models.features]
        X_scaled = models.scaler.transform(X)

        # Predict probabilities and calibrate
        raw_probs = models.model.predict_proba(X_scaled)[:, 1]
        probs = models.calibrator.predict(raw_probs.reshape(-1, 1))

        # Build response with risk categories
        results = []
        for p in probs:
            risk = (
                "Low Risk" if p < 0.35 else
                "Medium Risk" if p < 0.65 else
                "High Risk"
            )
            results.append(PredictResponse(probability=float(p), risk_category=risk))

        logger.info(f"/batch_predict | count={len(results)}")
        return BatchPredictResponse(results=results)

    except Exception as e:
        logger.error(f"/batch_predict ERROR | {str(e)}")
        raise HTTPException(status_code=500, detail="Batch prediction failed")


@app.get("/model/version")
def model_version():
    return models.version()


@app.post("/model/reload")
def model_reload():
    models.load_model()
    logger.info("Model reloaded")
    return {"status": "reloaded", "version": models.version()}
@app.get("/")
def root():
    return {
        "service": "QuantScore Credit Scoring API",
        "status": "running",
        "version": "1.0"
    }
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "model_info": models.version()
    }
