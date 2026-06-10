import threading
import logging
import pandas as pd

from app.services.regime_detection.regimes import RegimeDetector

logger = logging.getLogger(__name__)

_lock = threading.Lock()


class RegimeService:
    """
    Singleton-safe service that holds the latest regime state.
    Call update() periodically (e.g. daily via scheduler).
    Call get_current_regime() from API endpoints.

    stress_threshold raised to 0.030 so moderate volatility markets
    (1.0-2.5% daily vol) stay in normal regime. Only genuine crisis
    conditions (>1.5% daily vol) trigger stress.
    """

    def __init__(self, volatility_window: int = 20, stress_threshold: float = 0.030):
        self.detector = RegimeDetector(
            volatility_window=volatility_window,
            stress_threshold=stress_threshold,
        )
        self._latest_regime = self.detector._default_regime()

    def update(self, market_data: pd.DataFrame) -> dict:
        with _lock:
            self._latest_regime = self.detector.detect(market_data)
            logger.info(f"Regime updated: {self._latest_regime['regime']}")
        return self._latest_regime

    def get_current_regime(self) -> dict:
        return self._latest_regime


# Module-level singleton
regime_service = RegimeService()