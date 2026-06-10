from pydantic import BaseModel

from app.schemas.scoring import ScoringRequest


class ExplainabilityRequest(ScoringRequest):
    pass


class RiskDriver(BaseModel):
    feature: str
    impact: float


class ExplainabilityResponse(BaseModel):
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
    top_risk_drivers: list[RiskDriver]
    note: str