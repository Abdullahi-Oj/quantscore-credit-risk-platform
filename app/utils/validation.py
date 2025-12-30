# app/validation.py
from . import config as cfg

def validate_inputs(data: dict) -> list[str]:
    """
    Validate applicant inputs based on config constants.
    Returns a list of warnings. The prediction still proceeds,
    but flagged warnings indicate potential issues.
    """
    warnings = []

    # Age validation
    if not (cfg.AGE_MIN <= data["age"] <= cfg.AGE_MAX):
        warnings.append(f"Age outside allowed range ({cfg.AGE_MIN}-{cfg.AGE_MAX}).")

    # Income validation
    if data["income"] < cfg.INCOME_MIN:
        warnings.append(f"Income below minimum allowed ({cfg.INCOME_MIN}).")

    # Loan constraints
    if not (cfg.LOAN_MIN <= data["loan_amount"] <= cfg.LOAN_MAX):
        warnings.append(f"Loan amount outside recommended range ({cfg.LOAN_MIN}-{cfg.LOAN_MAX}).")

    # Installment-to-income
    if data["income"] > 0:
        inst_ratio = data["installment_per_month"] / data["income"]
        if inst_ratio > cfg.INSTALLMENT_INCOME_THRESHOLD:
            warnings.append(f"Installment exceeds {int(cfg.INSTALLMENT_INCOME_THRESHOLD*100)}% of income.")

    # Savings-to-loan ratio
    if data["loan_amount"] > 0:
        savings_ratio = data["savings"] / data["loan_amount"]
        if savings_ratio < cfg.SAVINGS_LOAN_MIN_RATIO:
            warnings.append(f"Savings too low relative to loan (savings_to_loan < {cfg.SAVINGS_LOAN_MIN_RATIO}).")

    # Previous defaults
    if data["previous_defaults"] > 0:
        warnings.append("Applicant has prior default history.")

    return warnings
