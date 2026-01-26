from . import config as cfg


def validate_inputs(data: dict) -> list[str]:
    """
    Validate applicant inputs based on config constants.

    Returns a list of warnings. The prediction still proceeds,
    but flagged warnings indicate potential issues.
    """
    warnings: list[str] = []

    # --------------------------
    # Age validation
    # --------------------------
    if not (cfg.AGE_MIN <= data["age"] <= cfg.AGE_MAX):
        warnings.append(
            f"Age outside allowed range "
            f"({cfg.AGE_MIN}-{cfg.AGE_MAX})."
        )

    # --------------------------
    # Income validation
    # --------------------------
    if data["income"] < cfg.INCOME_MIN:
        warnings.append(
            f"Income below minimum allowed "
            f"({cfg.INCOME_MIN})."
        )

    # --------------------------
    # Loan constraints
    # --------------------------
    if not (cfg.LOAN_MIN <= data["loan_amount"] <= cfg.LOAN_MAX):
        warnings.append(
            "Loan amount outside recommended range "
            f"({cfg.LOAN_MIN}-{cfg.LOAN_MAX})."
        )

    # --------------------------
    # Installment-to-income ratio
    # --------------------------
    if data["income"] > 0:
        installment_ratio = (
            data["installment_per_month"] / data["income"]
        )

        if installment_ratio > cfg.INSTALLMENT_INCOME_THRESHOLD:
            warnings.append(
                "Installment exceeds "
                f"{int(cfg.INSTALLMENT_INCOME_THRESHOLD * 100)}% "
                "of income."
            )

    # --------------------------
    # Savings-to-loan ratio
    # --------------------------
    if data["loan_amount"] > 0:
        savings_ratio = (
            data["savings"] / data["loan_amount"]
        )

        if savings_ratio < cfg.SAVINGS_LOAN_MIN_RATIO:
            warnings.append(
                "Savings too low relative to loan "
                "(savings_to_loan < "
                f"{cfg.SAVINGS_LOAN_MIN_RATIO})."
            )

    # --------------------------
    # Previous defaults
    # --------------------------
    if data["previous_defaults"] > 0:
        warnings.append(
            "Applicant has prior default history."
        )

    return warnings
