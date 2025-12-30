from pydantic import BaseModel, Field, validator
from typing import List

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

    class Config:
        schema_extra = {
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

# ==========================
# 🔹 Engineered / Internal Schema
# ==========================
class Applicant(BaseModel):
    age: int = Field(..., ge=18, le=75)
    income: float = Field(..., gt=0)
    savings: float = Field(..., ge=0)
    loan_amount: float = Field(..., gt=0)
    loan_term_months: int = Field(..., ge=1)
    dependents: int = Field(..., ge=0)
    credit_history: int
    gender: int
    married: int
    education: int
    self_employed: int
    transactions_per_month: int = Field(..., ge=0)
    previous_defaults: int = Field(..., ge=0)
    repayment_ratio: float = Field(..., ge=0.0, le=1.0)

    # Engineered features
    debt_to_income: float = Field(..., ge=0)
    installment_per_month: float = Field(..., ge=0)
    installment_to_income: float = Field(..., ge=0)

# ==========================
# 🔹 Response Schemas
# ==========================
class PredictResponse(BaseModel):
    probability: float
    risk_category: str

class BatchPredictResponse(BaseModel):
    results: List[PredictResponse]
