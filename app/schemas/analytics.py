from enum import Enum

from pydantic import BaseModel
from datetime import datetime


class RiskCategory(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DailyRequestCountResponse(BaseModel):
    counts: dict[str, int]


class AverageProbabilityResponse(BaseModel):
    average_probability: float


class RiskCategoryDistributionResponse(BaseModel):
    distribution: dict[RiskCategory, int]


class AnalyticsSummaryResponse(BaseModel):
    generated_at: datetime
    total_requests: int
    daily_requests: dict[str, int]
    average_probability: float
    risk_distribution: dict[RiskCategory, int]
