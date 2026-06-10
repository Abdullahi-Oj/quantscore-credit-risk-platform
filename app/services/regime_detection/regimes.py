import numpy as np
import pandas as pd


class RegimeDetector:
    """
    Detects market regime from price/returns data.

    Regime label is driven by dominant probability.
    Risk level is independently assigned by volatility bands.
    stress_threshold default raised to 0.025 to avoid over-sensitivity.

    Daily volatility bands:
        < 0.010           → low
        0.010 – 0.025     → medium
        > 0.025           → high
    """

    def __init__(
    self,
    volatility_window: int  = 20,
    stress_threshold: float = 0.030,  # raised from 0.025
):
        self.volatility_window = volatility_window
        self.stress_threshold  = stress_threshold

    def detect(self, market_data: pd.DataFrame) -> dict:
        if "returns" not in market_data.columns:
            raise ValueError("market_data must have a 'returns' column")

        returns = market_data["returns"].dropna()

        if len(returns) < self.volatility_window:
            return self._default_regime()

        rolling_vol = float(returns.rolling(self.volatility_window).std().iloc[-1])
        mean_return = float(returns.tail(self.volatility_window).mean())

        # Probabilities — regime label follows dominant probability
        stress_prob = round(min(rolling_vol / self.stress_threshold, 1.0), 4)
        normal_prob = round(1.0 - stress_prob, 4)
        regime      = "stress" if stress_prob > normal_prob else "normal"

        # Risk level — independent volatility bands
        risk_level = self._risk_level(rolling_vol)

        return {
            "regime":      regime,
            "volatility":  round(rolling_vol, 6),
            "mean_return": round(mean_return, 6),
            "risk_level":  risk_level,
            "market_state_probability": {
                "normal": normal_prob,
                "stress": stress_prob,
            },
        }

    def _risk_level(self, volatility: float) -> str:
        """Independent volatility band classifier."""
        if volatility < 0.010:
            return "low"
        elif volatility < 0.025:
            return "medium"
        else:
            return "high"

    def _default_regime(self) -> dict:
        return {
            "regime":      "normal",
            "volatility":  0.0,
            "mean_return": 0.0,
            "risk_level":  "low",
            "market_state_probability": {"normal": 1.0, "stress": 0.0},
        }