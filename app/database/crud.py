from sqlalchemy.orm import Session

from app.database.models import ScoringLog


def create_scoring_log(
    db: Session,
    request_id: str,
    endpoint: str,
    probability: float,
    risk_category: str,
    model_version: str,
    client_ip: str,
) -> ScoringLog:
    log = ScoringLog(
        request_id=request_id,
        endpoint=endpoint,
        probability=probability,
        risk_category=risk_category,
        model_version=model_version,
        client_ip=client_ip,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
