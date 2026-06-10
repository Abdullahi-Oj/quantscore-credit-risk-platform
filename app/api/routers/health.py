from fastapi import APIRouter, Depends

from app.api.deps import require_model_bundle
from app.ml.model_bundle import ModelBundle

router = APIRouter(tags=["health"])


@router.get("/")
def root():
    return {"message": "QuantScore API is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/version")
def version(model_bundle: ModelBundle = Depends(require_model_bundle)):
    return model_bundle.version()
