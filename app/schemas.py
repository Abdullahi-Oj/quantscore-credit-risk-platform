# app/schemas.py

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional

# ==========================
# 🔹 API Input Schema
# ==========================
class CreditData(BaseModel):
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

    @validator("CreditHistory", "Gender", "Married", "Education", "SelfEmployed")
    def binary_fields(cls, v):
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
                "RepaymentRatio": 0.8
            }
        }
    )

# ==========================
# 🔹 Response Schema
# ==========================
class CreditResponse(BaseModel):
    probability: float
    risk_category: str
    confidence: str
    reason: str
