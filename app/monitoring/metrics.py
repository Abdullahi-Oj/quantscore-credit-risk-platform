import numpy as np


def build_scoring_metrics(
    total_requests: int, error_count: int
) -> dict[str, float]:
    success_count = max(total_requests - error_count, 0)
    success_rate  = success_count / total_requests if total_requests else 0.0
    return {
        "total_requests": float(total_requests),
        "error_count":    float(error_count),
        "success_rate":   round(success_rate, 4),
    }


def brier_score(y_true: np.ndarray, probs: np.ndarray) -> float:
    """
    Measures calibration quality.
    0.0 = perfect, 0.25 = no skill, higher = worse.
    """
    return round(float(((probs - y_true) ** 2).mean()), 6)


def expected_calibration_error(
    y_true: np.ndarray, probs: np.ndarray, bins: int = 10
) -> float:
    """
    ECE — measures how well predicted probabilities match observed rates.
    Lower is better.
    """
    y_true = np.array(y_true)
    probs  = np.array(probs)

    bin_edges  = np.linspace(0.0, 1.0, bins + 1)
    ece        = 0.0
    n          = len(probs)

    for i in range(bins):
        mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
        if mask.sum() == 0:
            continue
        avg_conf     = probs[mask].mean()
        avg_accuracy = y_true[mask].mean()
        ece         += (mask.sum() / n) * abs(avg_conf - avg_accuracy)

    return round(float(ece), 6)


def hosmer_lemeshow_stat(
    y_true: np.ndarray, probs: np.ndarray, groups: int = 10
) -> dict:
    from scipy.stats import chi2

    y_true = np.array(y_true)
    probs  = np.array(probs)

    order      = np.argsort(probs)
    y_sorted   = y_true[order]
    p_sorted   = probs[order]
    group_size = len(probs) // groups

    hl_stat = 0.0
    for g in range(groups):
        start = g * group_size
        end   = (g + 1) * group_size if g < groups - 1 else len(probs)
        o_k   = y_sorted[start:end].sum()
        e_k   = p_sorted[start:end].sum()
        n_k   = end - start
        if e_k > 0 and (n_k - e_k) > 0:
            hl_stat += (o_k - e_k) ** 2 / (
                e_k * (1 - e_k / n_k)
            )

    p_value = 1 - chi2.cdf(hl_stat, df=groups - 2)
    return {
        "hl_stat":        round(float(hl_stat), 4),
        "p_value":        round(float(p_value), 4),
        "well_calibrated": bool(p_value >= 0.05),  # ← cast to Python bool
    }