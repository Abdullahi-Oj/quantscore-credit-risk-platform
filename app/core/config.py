from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # -----------------------------
    # Validation Rules
    # -----------------------------
    AGE_MIN: int = 18
    AGE_MAX: int = 75

    INCOME_MIN: int = 10_000
    SAVINGS_MIN: int = 0

    LOAN_MIN: int = 1_000
    LOAN_MAX: int = 5_000_000

    INSTALLMENT_INCOME_THRESHOLD: float = 0.6
    SAVINGS_LOAN_MIN_RATIO: float = 0.1
    REPAYMENT_RATIO_DEFAULT: int = 0

    # -----------------------------
    # Paths
    # -----------------------------
    MODEL_PATH: str = str(BASE_DIR / "models" / "xgb_calibrated.pkl")

    LOG_DIR: str = str(BASE_DIR / "logs")

    # -----------------------------
    # API
    # -----------------------------
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_KEY: str | None = None

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: str = "sqlite:///./quantscore.db"

    model_config = ConfigDict(
        env_prefix="QUANTSCORE_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()