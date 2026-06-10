class ThresholdEngine:
    """
    Adjusts approval thresholds and PD multipliers based on market regime.

    Normal regime: standard lending criteria
    Stress regime:  tighter approval, higher PD penalty
    """

    def __init__(self, config: dict = None):
        self.thresholds = config or {
            "normal": {"approval": 0.60, "pd_multiplier": 1.0},
            "stress": {"approval": 0.40, "pd_multiplier": 2.0},
        }

    def adjust_pd(self, base_pd: float, regime: str) -> float:
        multiplier = self.thresholds.get(regime, self.thresholds["normal"])["pd_multiplier"]
        return min(round(base_pd * multiplier, 4), 1.0)

    def get_approval_threshold(self, regime: str) -> float:
        return self.thresholds.get(regime, self.thresholds["normal"])["approval"]

    def get_decision(self, adjusted_pd: float, regime: str) -> str:
        threshold = self.get_approval_threshold(regime)
        return "approved" if adjusted_pd < threshold else "declined"