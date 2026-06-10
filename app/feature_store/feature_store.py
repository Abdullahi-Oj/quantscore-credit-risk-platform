import logging
from collections import defaultdict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Lightweight in-memory feature store.
    Computes rolling behavioural aggregates from transaction history.
    In production replace with Redis or PostgreSQL.
    """

    def __init__(self):
        self._store: dict[str, pd.DataFrame] = defaultdict(pd.DataFrame)

    def add_customer_history(
        self, customer_id: str, transactions: pd.DataFrame
    ) -> None:
        """
        Store transaction history for a customer.
        transactions must have columns: date, amount, type, balance
        type values: 'credit' or 'debit'
        """
        required = {"date", "amount", "type", "balance"}
        missing = required - set(transactions.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        transactions = transactions.copy()
        transactions["date"] = pd.to_datetime(transactions["date"])
        self._store[customer_id] = transactions.sort_values("date")
        logger.info(f"Stored {len(transactions)} transactions for {customer_id}")

    def has_customer(self, customer_id: str) -> bool:
        return customer_id in self._store and not self._store[customer_id].empty

    def compute_behavioral_features(
        self, customer_id: str, window_days: int = 90
    ) -> dict:
        """
        Compute rolling behavioural features for a customer.
        Returns empty dict if no history exists.
        """
        if not self.has_customer(customer_id):
            logger.warning(f"No history for customer {customer_id}")
            return {}

        df = self._store[customer_id]
        cutoff = df["date"].max() - pd.Timedelta(days=window_days)
        recent = df[df["date"] >= cutoff]

        if recent.empty:
            return {}

        credits = recent[recent["type"] == "credit"]["amount"]
        debits  = recent[recent["type"] == "debit"]["amount"]

        return {
            "inflow_volatility":        self._safe_std(credits),
            "outflow_volatility":       self._safe_std(debits),
            "transaction_acceleration": self._acceleration(recent),
            "balance_drawdown":         self._drawdown(recent["balance"]),
            "transaction_entropy":      self._entropy(recent["type"]),
            "avg_credit_amount":        float(credits.mean()) if not credits.empty else 0.0,
            "avg_debit_amount":         float(debits.mean())  if not debits.empty else 0.0,
            "transaction_count":        int(len(recent)),
            "credit_debit_ratio":       self._credit_debit_ratio(credits, debits),
        }

    def _safe_std(self, series: pd.Series) -> float:
        return float(series.std()) if len(series) > 1 else 0.0

    def _acceleration(self, df: pd.DataFrame) -> float:
        """Rate of change in transaction frequency — positive means accelerating."""
        if len(df) < 4:
            return 0.0
        mid = len(df) // 2
        first_half  = len(df.iloc[:mid])
        second_half = len(df.iloc[mid:])
        return float(second_half - first_half)

    def _drawdown(self, balance: pd.Series) -> float:
        """Min balance / max balance — lower means more stress."""
        max_bal = balance.max()
        if max_bal == 0:
            return 0.0
        return round(float(balance.min() / max_bal), 4)

    def _entropy(self, types: pd.Series) -> float:
        """Shannon entropy of transaction types — higher means more diverse."""
        counts = types.value_counts(normalize=True)
        return float(-np.sum(counts * np.log2(counts + 1e-9)))

    def _credit_debit_ratio(
        self, credits: pd.Series, debits: pd.Series
    ) -> float:
        total_debit = debits.sum()
        if total_debit == 0:
            return 1.0
        return round(float(credits.sum() / total_debit), 4)


# Module-level singleton
feature_store = FeatureStore()