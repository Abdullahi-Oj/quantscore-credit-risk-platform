from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    AverageProbabilityResponse,
    DailyRequestCountResponse,
    RiskCategory,
    RiskCategoryDistributionResponse,
)
from app.schemas.explainability import (
    ExplainabilityRequest,
    ExplainabilityResponse,
)
from app.schemas.scoring import ScoringRequest, ScoringResponse
from app.schemas.simulation import SimulationRequest

CreditData = ScoringRequest
CreditResponse = ScoringResponse

__all__ = [
    "ScoringRequest",
    "ScoringResponse",
    "ExplainabilityRequest",
    "ExplainabilityResponse",
    "RiskCategory",
    "DailyRequestCountResponse",
    "AverageProbabilityResponse",
    "RiskCategoryDistributionResponse",
    "AnalyticsSummaryResponse",
    "SimulationRequest",
    "CreditData",
    "CreditResponse",
]
