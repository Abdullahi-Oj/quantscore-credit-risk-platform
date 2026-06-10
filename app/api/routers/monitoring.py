import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends

from app.api.deps import require_model_bundle
from app.core.security import verify_api_key
from app.ml.model_bundle import ModelBundle
from app.monitoring.drift_detection import run_full_drift_report
from app.monitoring.metrics import (
    brier_score,
    expected_calibration_error,
    hosmer_lemeshow_stat,
)
from app.orchestration.scheduler import run_drift_check, set_reference_distribution

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
def monitoring_health(api_key: str = Depends(verify_api_key)):
    """Returns current monitoring system status."""
    _ = api_key
    return {"status": "ok", "monitoring": "active"}


@router.post("/drift/check")
def trigger_drift_check(
    api_key: str = Depends(verify_api_key),
    model_bundle: ModelBundle = Depends(require_model_bundle),
):
    """
    Runs a drift check comparing reference distribution
    against a simulated current window.
    In production replace current_data with recent DB predictions.
    """
    _ = api_key

    if model_bundle.sample_data is None:
        return {"status": "skipped", "reason": "no sample data in model artifact"}

    # Simulate current data with slight perturbation to mimic real drift
    np.random.seed(None)
    X_ref     = model_bundle.sample_data
    X_scaled  = model_bundle.scaler.transform(X_ref)

    # Add small noise to simulate incoming data distribution shift
    noise        = np.random.normal(0, 0.05, X_scaled.shape)
    X_current_sc = X_scaled + noise
    current_df   = pd.DataFrame(X_current_sc, columns=model_bundle.features)

    # Reference data
    ref_df = pd.DataFrame(X_scaled, columns=model_bundle.features)

    # Predictions on both
    ref_probs     = model_bundle.calibrator.predict(
        model_bundle.model.predict_proba(X_scaled)[:, 1]
    )
    current_probs = model_bundle.calibrator.predict(
        model_bundle.model.predict_proba(X_current_sc)[:, 1]
    )

    report = run_full_drift_report(
        reference=ref_df,
        current=current_df,
        features=model_bundle.features,
        reference_probs=np.array(ref_probs),
        current_probs=np.array(current_probs),
    )

    return report


@router.post("/calibration/evaluate")
def evaluate_calibration(api_key: str = Depends(verify_api_key)):
    """
    Runs calibration metrics on a synthetic sample.
    In production pass real observed defaults and predicted probs.
    """
    _ = api_key

    np.random.seed(42)
    n      = 500
    probs  = np.random.beta(2, 5, n)
    y_true = np.random.binomial(1, probs)

    return {
        "sample_size":       n,
        "brier_score":       brier_score(y_true, probs),
        "ece":               expected_calibration_error(y_true, probs),
        "hosmer_lemeshow":   hosmer_lemeshow_stat(y_true, probs),
        "note": "Replace synthetic data with real DB observations in production",
    }