import numpy as np
import pandas as pd

from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score, roc_curve


# --------------------------------------------------
# 1. AUC / ROC
# --------------------------------------------------


def compute_auc_roc(y_true, y_prob):
    """
    Measure ranking power of the model.
    """
    auc = roc_auc_score(y_true, y_prob)
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)

    return {
        "auc": auc,
        "roc_curve": {
            "fpr": fpr,
            "tpr": tpr,
            "thresholds": thresholds,
        },
    }


# --------------------------------------------------
# 2. KS Statistic
# --------------------------------------------------


def compute_ks_statistic(y_true, y_prob):
    """
    KS = maximum separation between good and bad borrowers.
    """
    good = y_prob[y_true == 0]
    bad = y_prob[y_true == 1]

    ks_stat, p_value = ks_2samp(good, bad)

    return {
        "ks_statistic": ks_stat,
        "p_value": p_value,
    }


# --------------------------------------------------
# 3. Default Rate by Risk Decile
# --------------------------------------------------


def default_rate_by_decile(y_true, y_prob, n_deciles=10):
    """
    Check monotonic risk ordering across score deciles.
    """
    df = pd.DataFrame(
        {
            "y_true": y_true,
            "y_prob": y_prob,
        }
    )

    df["decile"] = pd.qcut(
        df["y_prob"],
        q=n_deciles,
        labels=range(1, n_deciles + 1),
    )

    summary = (
        df.groupby("decile")
        .agg(
            count=("y_true", "count"),
            defaults=("y_true", "sum"),
            default_rate=("y_true", "mean"),
            avg_score=("y_prob", "mean"),
        )
        .sort_index()
    )

    return summary.reset_index()


# --------------------------------------------------
# 4. Population Stability Index (PSI)
# --------------------------------------------------


def population_stability_index(expected, actual, buckets=10):
    """
    Measure data drift between training and production.
    """

    def scale_range(series):
        return (series - series.min()) / (series.max() - series.min())

    expected = scale_range(pd.Series(expected))
    actual = scale_range(pd.Series(actual))

    breakpoints = np.linspace(0, 1, buckets + 1)

    expected_bins = (
        np.histogram(expected, breakpoints)[0] / len(expected)
    )
    actual_bins = (
        np.histogram(actual, breakpoints)[0] / len(actual)
    )

    psi = np.sum(
        (actual_bins - expected_bins)
        * np.log(
            (actual_bins + 1e-6)
            / (expected_bins + 1e-6)
        )
    )

    return psi


# --------------------------------------------------
# 5. Time-Based Validation
# --------------------------------------------------


def time_based_validation(
    df,
    date_col,
    target_col,
    prob_col,
    train_end_date,
):
    """
    Simulate real-world deployment using temporal splits.
    """
    train = df[df[date_col] <= train_end_date]
    test = df[df[date_col] > train_end_date]

    train_metrics = {
        "auc": roc_auc_score(
            train[target_col],
            train[prob_col],
        ),
        "ks": compute_ks_statistic(
            train[target_col],
            train[prob_col],
        )["ks_statistic"],
    }

    test_metrics = {
        "auc": roc_auc_score(
            test[target_col],
            test[prob_col],
        ),
        "ks": compute_ks_statistic(
            test[target_col],
            test[prob_col],
        )["ks_statistic"],
    }

    psi = population_stability_index(
        train[prob_col],
        test[prob_col],
    )

    return {
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "psi": psi,
    }


# --------------------------------------------------
# 6. One-Call Validation Runner
# --------------------------------------------------


def run_full_validation(y_true, y_prob):
    """
    Convenience wrapper for quick evaluation.
    """
    return {
        "auc_roc": compute_auc_roc(y_true, y_prob),
        "ks": compute_ks_statistic(y_true, y_prob),
        "default_rate_by_decile": default_rate_by_decile(
            y_true,
            y_prob,
        ),
    }
