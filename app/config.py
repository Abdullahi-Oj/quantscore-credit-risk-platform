# -----------------------------
# QuantScore Config Constants
# -----------------------------

import os

# -----------------------------
# Applicant constraints
# -----------------------------
AGE_MIN = 18
AGE_MAX = 75

INCOME_MIN = 10_000
SAVINGS_MIN = 0

LOAN_MIN = 1_000
LOAN_MAX = 5_000_000

INSTALLMENT_INCOME_THRESHOLD = 0.6  # 60%
SAVINGS_LOAN_MIN_RATIO = 0.1        # At least 10%
REPAYMENT_RATIO_DEFAULT = 0

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "models", "xgb_calibrated.pkl"
)
LOG_DIR = os.path.join(BASE_DIR, "app", "logs")

# -----------------------------
# API (environment override)
# -----------------------------
API_HOST = os.getenv("QUANTSCORE_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("QUANTSCORE_API_PORT", 8000))
