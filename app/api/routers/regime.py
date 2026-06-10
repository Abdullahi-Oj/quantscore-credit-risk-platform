from fastapi import APIRouter, Depends

from app.core.security import verify_api_key
from app.services.regime_detection.service import regime_service
from app.orchestration.scheduler import run_regime_update

router = APIRouter(prefix="/regime", tags=["regime"])


@router.get("/current")
def get_current_regime(
    api_key: str = Depends(verify_api_key),
):
    """Returns the current market regime and volatility state."""
    _ = api_key
    return regime_service.get_current_regime()


@router.post("/refresh")
def refresh_regime(
    api_key: str = Depends(verify_api_key),
):
    """Manually triggers a regime update. Useful for testing."""
    _ = api_key
    run_regime_update()
    return regime_service.get_current_regime()