import logging

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


def population_stability_index(
    expected: np.ndarray, actual: np.ndarray, bins: int = 10
) -> float:
    expected = np.array(expected)
    actual   = np.array(actual)

    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
    breakpoints = np.unique(breakpoints)

    expected_counts, _ = np.histogram(expected, bins=breakpoints)
    actual_counts,   _ = np.histogram(actual,   bins=breakpoints)

    expected_pct = expected_counts / len(expected)
    actual_pct   = actual_counts   / len(actual)

    psi = np.sum(
        (actual_pct - expected_pct)
        * np.log((actual_pct + 1e-6) / (expected_pct + 1e-6))
    )
    return round(float(psi), 6)


def feature_drift(
    reference: pd.DataFrame, current: pd.DataFrame, feature: str
) -> dict:
    if feature not in reference.columns or feature not in current.columns:
        return {"feature": feature, "error": "feature not found"}

    stat, p = ks_2samp(
        reference[feature].dropna(),
        current[feature].dropna(),
    )
    return {
        "feature":    feature,
        "ks_stat":    round(float(stat), 6),
        "p_value":    round(float(p), 6),
        "drift_flag": bool(p < 0.05),           # ← cast to Python bool
    }


def prediction_drift(
    reference_probs: np.ndarray, current_probs: np.ndarray
) -> dict:
    stat, p = ks_2samp(reference_probs, current_probs)
    psi      = population_stability_index(reference_probs, current_probs)
    return {
        "ks_stat":    round(float(stat), 6),
        "p_value":    round(float(p), 6),
        "psi":        psi,
        "drift_flag": bool(p < 0.05 or psi >= 0.25),  # ← cast to Python bool
    }


def run_full_drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    features: list[str],
    reference_probs: np.ndarray = None,
    current_probs: np.ndarray   = None,
) -> dict:
    feature_results = [
        feature_drift(reference, current, f) for f in features
    ]

    drifted = [r["feature"] for r in feature_results if r.get("drift_flag")]

    report = {
        "features_checked": len(features),
        "features_drifted": len(drifted),
        "drifted_features": drifted,
        "feature_details":  feature_results,
    }

    if reference_probs is not None and current_probs is not None:
        report["prediction_drift"] = prediction_drift(
            reference_probs, current_probs
        )

    return report