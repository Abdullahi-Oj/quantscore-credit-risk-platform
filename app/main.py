from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.api.routers.health import router as health_router
from app.api.routers.analytics import router as analytics_router
from app.api.routers.scoring import router as scoring_router
from app.api.routers.regime import router as regime_router
from app.api.routers.monitoring import router as monitoring_router
from app.core.rate_limit import limiter, rate_limit_handler
from app.database import init_db
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.tracing import RequestTracingMiddleware
from app.api.deps import get_model_bundle
from app.orchestration.scheduler import run_regime_update, start_scheduler

app = FastAPI(
    title="QuantScore Credit Scoring API",
    description="AI-powered credit risk scoring with explainability",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTracingMiddleware)
app.include_router(health_router)
app.include_router(scoring_router)
app.include_router(analytics_router)
app.include_router(regime_router)
app.include_router(monitoring_router)


@app.on_event("startup")
def startup_event() -> None:
    import numpy as np
    import pandas as pd
    from app.orchestration.scheduler import set_reference_distribution

    init_db()
    bundle = get_model_bundle()
    run_regime_update()
    start_scheduler()

    # Set reference distribution from sample data in model artifact
    if bundle.sample_data is not None:
        X_ref    = bundle.sample_data
        raw      = bundle.model.predict_proba(bundle.scaler.transform(X_ref))[:, 1]
        ref_probs = bundle.calibrator.predict(raw)
        set_reference_distribution(
            probs=np.array(ref_probs),
            data=pd.DataFrame(bundle.scaler.transform(X_ref), columns=bundle.features),
        )