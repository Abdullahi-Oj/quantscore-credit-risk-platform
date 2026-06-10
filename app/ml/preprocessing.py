from typing import Any

import pandas as pd


def transform_input(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "Age":                  payload["Age"],
        "Gender":               payload["Gender"],
        "MonthlyIncome":        payload["MonthlyIncome"],
        "Savings":              payload.get("Savings", 0),
        "LoanAmount":           payload["LoanAmount"],
        "LoanDuration":         payload["LoanDuration"],
        "Dependents":           payload["Dependents"],
        "CreditHistory":        payload["CreditHistory"],
        "Married":              payload["Married"],
        "Education":            payload["Education"],
        "SelfEmployed":         payload["SelfEmployed"],
        "TransactionsPerMonth": payload.get("TransactionsPerMonth", 0),
        "PreviousDefaults":     payload.get("PreviousDefaults", 0),
        "RepaymentRatio":       payload.get("RepaymentRatio", 0.0),
    }


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["InstallmentPerMonth"] = out["LoanAmount"] / out["LoanDuration"].replace(0, 1)
    out["InstallmentToIncome"] = out["InstallmentPerMonth"] / out["MonthlyIncome"].replace(0, 1)
    out["DebtToIncome"]        = out["LoanAmount"] / out["MonthlyIncome"].replace(0, 1)
    out["SavingsToLoan"]       = out["Savings"] / (out["LoanAmount"] + 1)
    return out


def interpret_result(probability: float) -> dict:
    """
    Converts PD to risk category, confidence, reason,
    credit score (300-850), and decision band.

    Credit score formula:
        score = 850 - (probability * 550)
        PD=0.0001 → ~850, PD=0.50 → ~575, PD=0.9999 → ~300

    Decision bands:
        PD < 0.20       → Approved
        0.20 <= PD < 0.40 → Manual Review
        PD >= 0.40      → Declined
    """
    # Credit score — inverse of PD, scaled to 300-850
    credit_score = int(round(850 - (probability * 550)))
    credit_score = max(300, min(850, credit_score))

    # Decision band
    if probability < 0.20:
        decision_band = "approved"
    elif probability < 0.40:
        decision_band = "manual_review"
    else:
        decision_band = "declined"

    # Risk category
    if probability < 0.20:
        return {
            "risk_category": "Low",
            "confidence":    "High",
            "reason":        "Strong repayment profile",
            "credit_score":  credit_score,
            "decision_band": decision_band,
        }
    if probability < 0.50:
        return {
            "risk_category": "Medium",
            "confidence":    "Moderate",
            "reason":        "Mixed risk signals detected",
            "credit_score":  credit_score,
            "decision_band": decision_band,
        }
    return {
        "risk_category": "High",
        "confidence":    "High",
        "reason":        "High likelihood of default",
        "credit_score":  credit_score,
        "decision_band": decision_band,
    }