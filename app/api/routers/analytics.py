from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_session
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    AverageProbabilityResponse,
    DailyRequestCountResponse,
    RiskCategoryDistributionResponse,
)
from app.services.analytics_service import (
    get_average_probability,
    get_daily_request_count,
    get_risk_category_distribution,
    get_summary_metrics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/daily-requests", response_model=DailyRequestCountResponse)
def daily_requests(db: Session = Depends(get_session)):
    return {"counts": get_daily_request_count(db)}


@router.get(
    "/average-probability", response_model=AverageProbabilityResponse
)
def average_probability(db: Session = Depends(get_session)):
    return {"average_probability": get_average_probability(db)}


@router.get(
    "/risk-distribution", response_model=RiskCategoryDistributionResponse
)
def risk_distribution(db: Session = Depends(get_session)):
    return {"distribution": get_risk_category_distribution(db)}


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(db: Session = Depends(get_session)):
    return get_summary_metrics(db)
