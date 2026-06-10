import logging

import numpy as np
import pandas as pd

from app.services.regime_detection.service import regime_service
from app.monitoring.drift_detection import run_full_drift_report

logger = logging.getLogger(__name__)

# Reference distribution stored at startup — compare against daily predictions
_reference_probs: np.ndarray = None
_reference_data:  pd.DataFrame = None


def generate_mock_market_data(n: int = 100) -> pd.DataFrame:
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.015, n)
    return pd.DataFrame({"returns": returns})


def set_reference_distribution(
    probs: np.ndarray, data: pd.DataFrame
) -> None:
    """Call this once after model loads to set the baseline."""
    global _reference_probs, _reference_data
    _reference_probs = probs
    _reference_data  = data
    logger.info("Reference distribution set for drift monitoring.")


def run_drift_check(
    current_probs: np.ndarray = None,
    current_data: pd.DataFrame = None,
    features: list[str] = None,
) -> dict:
    """Run drift check against reference distribution."""
    if _reference_probs is None:
        logger.warning("No reference distribution set — skipping drift check.")
        return {"status": "skipped", "reason": "no reference distribution"}

    if current_probs is None or current_data is None:
        logger.warning("No current data provided — skipping drift check.")
        return {"status": "skipped", "reason": "no current data"}

    report = run_full_drift_report(
        reference=_reference_data,
        current=current_data,
        features=features or [],
        reference_probs=_reference_probs,
        current_probs=current_probs,
    )

    if report["features_drifted"] > 0:
        logger.warning(
            f"Drift detected in {report['features_drifted']} features: "
            f"{report['drifted_features']}"
        )
    else:
        logger.info("Drift check passed — no significant drift detected.")

    return report


def run_regime_update() -> None:
    try:
        market_data = generate_mock_market_data()
        result = regime_service.update(market_data)
        logger.info(f"Regime update complete: {result['regime']}")
    except Exception:
        logger.exception("Regime update failed")


def start_scheduler() -> None:
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(run_regime_update, "cron", hour=8, minute=0)
        scheduler.add_job(
            lambda: run_drift_check(), "cron", hour=8, minute=30
        )
        scheduler.start()
        logger.info("Scheduler started — regime at 08:00, drift at 08:30")
    except ImportError:
        logger.warning("apscheduler not installed — scheduler disabled")