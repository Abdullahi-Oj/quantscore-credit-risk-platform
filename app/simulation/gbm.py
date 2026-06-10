# app/simulation/gbm.py

import numpy as np
from typing import Optional, Dict


class IncomeGBMSimulator:
    """
    Simulates borrower income paths using GBM + macro shocks.
    Designed for credit stress testing.
    """

    def __init__(
        self,
        mu: float = 0.05,
        sigma: float = 0.25,
        seed: Optional[int] = None,
    ):
        """
        Parameters
        ----------
        mu : float
            Expected income growth (annualized)
        sigma : float
            Income volatility
        seed : int
            Random seed (auditability)
        """

        self.mu = mu
        self.sigma = sigma
        self.seed = seed

        if seed is not None:
            np.random.seed(seed)

    # ------------------------------------------------

    def _apply_shock(
        self,
        paths: np.ndarray,
        shock: Dict,
        dt: float,
    ) -> np.ndarray:
        """
        Inject macro / personal shocks into income paths
        """

        shock_type = shock.get("type")

        if shock_type == "job_loss":

            start = shock.get("start_step", 0)
            duration = shock.get("duration", 3)
            severity = shock.get("severity", 0.6)

            for t in range(start, start + duration):
                paths[:, t:] *= (1 - severity)

        # --------------------------------------------

        elif shock_type == "inflation":

            erosion = shock.get("erosion", 0.02)

            erosion_factor = np.exp(-erosion * dt)

            for t in range(1, paths.shape[1]):
                paths[:, t] *= erosion_factor ** t

        # --------------------------------------------

        elif shock_type == "health":

            step = shock.get("step", 5)
            severity = shock.get("severity", 0.3)

            paths[:, step:] *= (1 - severity)

        # --------------------------------------------

        elif shock_type == "policy":

            vol_spike = shock.get("vol_spike", 1.5)

            paths *= np.exp(
                np.random.normal(
                    0,
                    self.sigma * vol_spike,
                    size=paths.shape,
                )
            )

        return paths

    # ------------------------------------------------

    def simulate(
        self,
        income_0: float,
        T: float = 2.0,
        n_steps: int = 24,
        n_sims: int = 5000,
        shock: Optional[Dict] = None,
    ) -> np.ndarray:
        """
        Run GBM income simulation

        Returns
        -------
        paths : ndarray (n_sims, n_steps+1)
        """

        dt = T / n_steps

        paths = np.zeros((n_sims, n_steps + 1))
        paths[:, 0] = income_0

        Z = np.random.standard_normal((n_sims, n_steps))

        drift = (self.mu - 0.5 * self.sigma ** 2) * dt
        diffusion = self.sigma * np.sqrt(dt)

        # GBM evolution
        for t in range(1, n_steps + 1):

            paths[:, t] = (
                paths[:, t - 1]
                * np.exp(drift + diffusion * Z[:, t - 1])
            )

        # Apply stress
        if shock:
            paths = self._apply_shock(paths, shock, dt)

        return paths
