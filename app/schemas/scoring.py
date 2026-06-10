from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScoringRequest(BaseModel):
    Age: int = Field(..., ge=18, le=75)
    MonthlyIncome: float = Field(..., gt=0)
    LoanAmount: float = Field(..., gt=0)
    LoanDuration: int = Field(..., ge=1)
    Dependents: int = Field(..., ge=0)
    CreditHistory: int
    Gender: int
    Married: int
    Education: int
    SelfEmployed: int
    Savings: float = 0
    TransactionsPerMonth: int = 0
    PreviousDefaults: int = 0
    RepaymentRatio: float = 0.0

    @field_validator(
        "CreditHistory",
        "Gender",
        "Married",
        "Education",
        "SelfEmployed",
    )
    @classmethod
    def binary_fields(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("Field must be 0 or 1")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Age": 30,
                "MonthlyIncome": 250000,
                "LoanAmount": 800000,
                "LoanDuration": 12,
                "Dependents": 0,
                "CreditHistory": 1,
                "Gender": 1,
                "Married": 0,
                "Education": 1,
                "SelfEmployed": 0,
                "Savings": 500000,
                "TransactionsPerMonth": 10,
                "PreviousDefaults": 0,
                "RepaymentRatio": 0.8,
            }
        }
    )


class ScoringResponse(BaseModel):
    probability: float
    credit_score: int
    risk_category: str
    confidence: str
    reason: str
    decision_band: str
    regime: str
    base_probability: float
    regime_adjustment: float
    threshold: float
    decision: str
    decision_reason: str

class BatchScoringRequest(BaseModel):
    applicants: List[ScoringRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of applicants to score. Maximum 100 per request.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "applicants": [
                    {
                        "Age": 30,
                        "MonthlyIncome": 250000,
                        "LoanAmount": 800000,
                        "LoanDuration": 12,
                        "Dependents": 0,
                        "CreditHistory": 1,
                        "Gender": 1,
                        "Married": 0,
                        "Education": 1,
                        "SelfEmployed": 0,
                        "Savings": 500000,
                        "TransactionsPerMonth": 10,
                        "PreviousDefaults": 0,
                        "RepaymentRatio": 0.8,
                    },
                    {
                        "Age": 45,
                        "MonthlyIncome": 80000,
                        "LoanAmount": 1200000,
                        "LoanDuration": 24,
                        "Dependents": 3,
                        "CreditHistory": 0,
                        "Gender": 0,
                        "Married": 1,
                        "Education": 0,
                        "SelfEmployed": 1,
                        "Savings": 50000,
                        "TransactionsPerMonth": 4,
                        "PreviousDefaults": 1,
                        "RepaymentRatio": 0.4,
                    },
                ]
            }
        }
    )


class BatchScoringResult(BaseModel):
    applicant_index: int
    request_id: str
    probability: float
    credit_score: int
    risk_category: str
    confidence: str
    reason: str
    decision_band: str
    regime: str
    base_probability: float
    regime_adjustment: float
    threshold: float
    decision: str
    decision_reason: str

class BatchScoringResponse(BaseModel):
    total: int
    results: List[BatchScoringResult]