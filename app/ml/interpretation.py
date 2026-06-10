import numpy as np

def interpret_result(probability: float) -> dict:
    # Log-odds scaling — spreads scores more evenly across the range
    # Clamp probability to avoid log(0)
    p     = max(min(probability, 0.9999), 0.0001)
    odds  = p / (1 - p)
    log_odds = np.log(odds)

    # Map log-odds to 300-850
    # log_odds range: approx -9 (very safe) to +9 (very risky)
    lo_min, lo_max = -9.0, 9.0
    normalized     = (log_odds - lo_min) / (lo_max - lo_min)
    normalized     = max(0.0, min(1.0, normalized))
    credit_score   = int(round(850 - (normalized * 550)))
    credit_score   = max(300, min(850, credit_score))

    # Decision band
    if probability < 0.20:
        decision_band = "approved"
    elif probability < 0.40:
        decision_band = "manual_review"
    else:
        decision_band = "declined"

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