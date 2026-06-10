from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.models import ScoringLog
from app.schemas.analytics import RiskCategory


def get_daily_request_count(db: Session) -> dict[str, int]:
    rows = (
        db.query(
            func.date(ScoringLog.created_at).label("day"),
            func.count(ScoringLog.id).label("total"),
        )
        .group_by(func.date(ScoringLog.created_at))
        .order_by(func.date(ScoringLog.created_at))
        .all()
    )
    return {str(row.day): int(row.total) for row in rows}


def get_average_probability(db: Session) -> float:
    avg_value = db.query(func.avg(ScoringLog.probability)).scalar()
    return float(avg_value or 0.0)


def get_total_requests(db: Session) -> int:
    total = db.query(func.count(ScoringLog.id)).scalar()
    return int(total or 0)


def get_risk_category_distribution(db: Session) -> dict[RiskCategory, int]:
    rows = (
        db.query(
            ScoringLog.risk_category,
            func.count(ScoringLog.id).label("total"),
        )
        .group_by(ScoringLog.risk_category)
        .all()
    )
    distribution: dict[RiskCategory, int] = {
        RiskCategory.LOW: 0,
        RiskCategory.MEDIUM: 0,
        RiskCategory.HIGH: 0,
    }
    for category, total in rows:
        if category in {RiskCategory.LOW.value, RiskCategory.MEDIUM.value, RiskCategory.HIGH.value}:
            distribution[RiskCategory(category)] = int(total)
    return distribution


def get_summary_metrics(db: Session) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc),
        "total_requests": get_total_requests(db),
        "daily_requests": get_daily_request_count(db),
        "average_probability": get_average_probability(db),
        "risk_distribution": get_risk_category_distribution(db),
    }
