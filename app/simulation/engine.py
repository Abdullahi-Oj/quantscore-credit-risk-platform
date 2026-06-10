# app/simulation/engine.py

import numpy as np
import pandas as pd
from typing import Dict, Optional

from app.simulation.gbm import IncomeGBMSimulator
from app.utils.model_loader import ModelBundle


class StressTestEngine:
    """
    Runs Monte Carlo credit stress testing
    using income simulations + ML rescoring
    """

    def __init__(
        self,
        model_bundle: ModelBundle,
        seed: Optional[int] = None,
    ):

        self.models = model_bundle
        self.simulator = IncomeGBMSimulator(seed=seed)

    # ------------------------------------------------

    def _rebuild_features(
        self,
        base_row: pd.Series,
        income_paths: np.ndarray,
    ) -> pd.DataFrame:
        """
        Recompute features under stressed income
        """

        n_sims, n_steps = income_paths.shape

        final_income = income_paths[:, -1]

        df = pd.DataFrame(
            np.repeat(base_row.values[None, :], n_sims, axis=0),
            columns=base_row.index,
        )

        # Replace income with stressed values
        df["income"] = final_income

        # Recompute ratios (same logic as main.py)
        df["installment_per_month"] = (
            df["loan_amount"] / df["loan_term_months"].replace(0, 1)
        )

        df["installment_to_income"] = (
            df["installment_per_month"] / df["income"].replace(0, 1)
        )

        df["savings_to_loan"] = df["savings"] / (df["loan_amount"] + 1)

        df["debt_to_income"] = (
            df["loan_amount"] / df["income"].replace(0, 1)
        )

        return df

    # ------------------------------------------------

    def run_stress_test(
        self,
        borrower_data: Dict,
        shock: Optional[Dict] = None,
        n_sims: int = 10000,
        T: float = 2.0,
        n_steps: int = 24,
    ) -> Dict:
        """
        Run Monte Carlo stress test
        """

        base_df = pd.DataFrame([borrower_data])

        income_0 = base_df["income"].iloc[0]

        # 1️⃣ Simulate income
        paths = self.simulator.simulate(
            income_0=income_0,
            T=T,
            n_steps=n_steps,
            n_sims=n_sims,
            shock=shock,
        )

        # 2️⃣ Rebuild features
        stressed_df = self._rebuild_features(
            base_df.iloc[0],
            paths,
        )

        # 3️⃣ Scale
        X = self.models.scaler.transform(
            stressed_df[self.models.features]
        )

        # 4️⃣ Predict PD
        raw_pd = self.models.model.predict_proba(X)[:, 1]

        pd_vals = self.models.calibrator.predict(
            raw_pd.reshape(-1, 1)
        )

        # 5️⃣ Risk metrics
        results = {
            "mean_pd": float(np.mean(pd_vals)),
            "median_pd": float(np.median(pd_vals)),
            "p90_pd": float(np.percentile(pd_vals, 90)),
            "p99_pd": float(np.percentile(pd_vals, 99)),
            "worst_pd": float(np.max(pd_vals)),
        }

        return results
