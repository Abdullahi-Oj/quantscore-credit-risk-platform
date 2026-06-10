import logging

import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.ml.interpretation import interpret_result
from app.ml.model_bundle import ModelBundle
from app.ml.preprocessing import engineer_features, transform_input
from app.schemas.scoring import ScoringRequest
from app.services.regime_detection.service import regime_service
from app.services.threshold_engine.adjuster import ThresholdEngine

logger = logging.getLogger(__name__)

_threshold_engine = ThresholdEngine()


def prepare_features(data: ScoringRequest, model_bundle: ModelBundle):
    df = pd.DataFrame([transform_input(data.model_dump())])
    df = engineer_features(df)
    try:
        X = df[model_bundle.features]
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail="Feature mismatch with trained model"
        ) from exc
    X_scaled = model_bundle.scaler.transform(X)
    return X, X_scaled


def _apply_regime(calibrated_prob: float) -> dict:
    regime        = regime_service.get_current_regime()
    regime_label  = regime["regime"]
    adjusted_prob = _threshold_engine.adjust_pd(calibrated_prob, regime_label)
    threshold     = _threshold_engine.get_approval_threshold(regime_label)

    # Clip to avoid hard 0.0 and 1.0 — standard credit risk practice
    adjusted_prob = float(np.clip(adjusted_prob, 0.0001, 0.9999))

    decision      = _threshold_engine.get_decision(adjusted_prob, regime_label)
    adjustment    = round(adjusted_prob - calibrated_prob, 4)

    if decision.lower() == "approved":
        decision_reason = (
            f"Adjusted PD {adjusted_prob:.4f} is below the "
            f"{regime_label}-regime approval threshold of {threshold}"
        )
    elif decision.lower() in ("manual_review", "review", "conditional"):
        decision_reason = (
            f"Adjusted PD {adjusted_prob:.4f} falls within the "
            f"{regime_label}-regime review range around threshold {threshold}"
        )
    else:
        decision_reason = (
            f"Adjusted PD {adjusted_prob:.4f} exceeds the "
            f"{regime_label}-regime rejection threshold of {threshold}"
        )

    return {
        "regime":            regime_label,
        "base_probability":  round(float(np.clip(calibrated_prob, 0.0001, 0.9999)), 4),
        "regime_adjustment": adjustment,
        "probability":       round(adjusted_prob, 4),
        "threshold":         threshold,
        "decision":          decision,
        "decision_reason":   decision_reason,
    }


def score(data: ScoringRequest, model_bundle: ModelBundle) -> dict:
    try:
        _, X_scaled     = prepare_features(data, model_bundle)
        raw_prob        = model_bundle.model.predict_proba(X_scaled)[0][1]
        calibrated_prob = float(model_bundle.calibrator.predict([[raw_prob]])[0])
        regime_fields   = _apply_regime(calibrated_prob)
        interp          = interpret_result(regime_fields["probability"])

        return {
            "probability":       regime_fields["probability"],
            "credit_score":      interp["credit_score"],
            "risk_category":     interp["risk_category"],
            "confidence":        interp["confidence"],
            "reason":            interp["reason"],
            "decision_band":     interp["decision_band"],
            "regime":            regime_fields["regime"],
            "base_probability":  regime_fields["base_probability"],
            "regime_adjustment": regime_fields["regime_adjustment"],
            "threshold":         regime_fields["threshold"],
            "decision":          regime_fields["decision"],
            "decision_reason":   regime_fields["decision_reason"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc


def explain_score(data: ScoringRequest, model_bundle: ModelBundle) -> dict:
    try:
        X, X_scaled     = prepare_features(data, model_bundle)
        raw_prob        = model_bundle.model.predict_proba(X_scaled)[0][1]
        calibrated_prob = float(model_bundle.calibrator.predict([[raw_prob]])[0])
        regime_fields   = _apply_regime(calibrated_prob)
        interp          = interpret_result(regime_fields["probability"])

        shap_values = model_bundle.explainer.shap_values(X_scaled)
        if isinstance(shap_values, list):
            shap_contrib = shap_values[1][0]
        else:
            shap_contrib = shap_values[0]

        feature_impact = dict(zip(model_bundle.features, shap_contrib))
        top_features   = sorted(
            feature_impact.items(), key=lambda x: abs(x[1]), reverse=True
        )[:5]

        return {
            "probability":       regime_fields["probability"],
            "credit_score":      interp["credit_score"],
            "risk_category":     interp["risk_category"],
            "confidence":        interp["confidence"],
            "reason":            interp["reason"],
            "decision_band":     interp["decision_band"],
            "regime":            regime_fields["regime"],
            "base_probability":  regime_fields["base_probability"],
            "regime_adjustment": regime_fields["regime_adjustment"],
            "threshold":         regime_fields["threshold"],
            "decision":          regime_fields["decision"],
            "decision_reason":   regime_fields["decision_reason"],
            "top_risk_drivers": [
                {"feature": f, "impact": float(v)}
                for f, v in top_features
            ],
            "note": "SHAP explains base model output (pre-calibration)",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Explain failed")
        raise HTTPException(status_code=500, detail="Explain failed") from exc


def feature_importance(model_bundle: ModelBundle) -> dict:
    try:
        if model_bundle.sample_data is None:
            raise HTTPException(status_code=400, detail="No sample data available")

        X        = model_bundle.sample_data[model_bundle.features]
        X_scaled = model_bundle.scaler.transform(X)
        shap_values = model_bundle.explainer.shap_values(X_scaled)

        if isinstance(shap_values, list):
            values = shap_values[1]
        else:
            values = shap_values

        mean_importance = np.abs(values).mean(axis=0)
        importance = {
            feature: float(value)                    # ← cast to Python float
            for feature, value in zip(model_bundle.features, mean_importance)
        }
        return dict(sorted(importance.items(), key=lambda x: -x[1]))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Feature importance failed")
        raise HTTPException(
            status_code=500, detail="Feature importance failed"
        ) from exc