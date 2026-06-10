import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_model_bundle
from app.core.rate_limit import limiter
from app.core.security import verify_api_key
from app.database.crud import create_scoring_log
from app.database.session import get_session
from app.ml.model_bundle import ModelBundle
from app.schemas.explainability import ExplainabilityRequest, ExplainabilityResponse
from app.schemas.scoring import (
    BatchScoringRequest,
    BatchScoringResponse,
    BatchScoringResult,
    ScoringRequest,
    ScoringResponse,
)
from app.services.scoring_service import explain_score, feature_importance, score

router = APIRouter(tags=["scoring"])


@router.post("/predict", response_model=ScoringResponse)
@limiter.limit("100/minute")
def predict(
    request: Request,
    data: ScoringRequest,
    api_key: str = Depends(verify_api_key),
    model_bundle: ModelBundle = Depends(require_model_bundle),
    db: Session = Depends(get_session),
):
    _ = api_key
    result = score(data, model_bundle)
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    create_scoring_log(
        db=db,
        request_id=trace_id,
        endpoint="/predict",
        probability=result["probability"],
        risk_category=result["risk_category"],
        model_version=model_bundle.version().get("model_file", "unknown"),
        client_ip=request.client.host if request.client else "unknown",
    )
    return result


@router.post("/batch_predict", response_model=BatchScoringResponse)
@limiter.limit("20/minute")
def batch_predict(
    request: Request,
    data: BatchScoringRequest,
    api_key: str = Depends(verify_api_key),
    model_bundle: ModelBundle = Depends(require_model_bundle),
    db: Session = Depends(get_session),
):
    _ = api_key
    results = []
    client_ip = request.client.host if request.client else "unknown"
    model_version = model_bundle.version().get("model_file", "unknown")
    batch_trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))

    for idx, applicant in enumerate(data.applicants):
        result = score(applicant, model_bundle)
        request_id = f"{batch_trace_id}-{idx}"

        create_scoring_log(
            db=db,
            request_id=request_id,
            endpoint="/batch_predict",
            probability=result["probability"],
            risk_category=result["risk_category"],
            model_version=model_version,
            client_ip=client_ip,
        )

        results.append(
    BatchScoringResult(
        applicant_index=idx,
        request_id=request_id,
        probability=result["probability"],
        credit_score=result["credit_score"],
        risk_category=result["risk_category"],
        confidence=result["confidence"],
        reason=result["reason"],
        decision_band=result["decision_band"],
        regime=result["regime"],
        base_probability=result["base_probability"],
        regime_adjustment=result["regime_adjustment"],
        threshold=result["threshold"],
        decision=result["decision"],
        decision_reason=result["decision_reason"],
    )
)
    return BatchScoringResponse(total=len(results), results=results)


@router.post("/explain", response_model=ExplainabilityResponse)
@limiter.limit("50/minute")
def explain(
    request: Request,
    data: ExplainabilityRequest,
    api_key: str = Depends(verify_api_key),
    model_bundle: ModelBundle = Depends(require_model_bundle),
    db: Session = Depends(get_session),
):
    _ = api_key
    result = explain_score(data, model_bundle)
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    create_scoring_log(
        db=db,
        request_id=trace_id,
        endpoint="/explain",
        probability=result["probability"],
        risk_category=result["risk_category"],
        model_version=model_bundle.version().get("model_file", "unknown"),
        client_ip=request.client.host if request.client else "unknown",
    )
    return result


@router.get("/feature-importance")
def get_feature_importance(
    api_key: str = Depends(verify_api_key),
    model_bundle: ModelBundle = Depends(require_model_bundle),
):
    _ = api_key
    return feature_importance(model_bundle)