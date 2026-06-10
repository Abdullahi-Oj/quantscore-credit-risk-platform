import logging
import threading

from fastapi import HTTPException

from app.ml.model_bundle import ModelBundle

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_model_bundle: ModelBundle | None = None


def get_model_bundle() -> ModelBundle:
    global _model_bundle
    if _model_bundle is None:
        with _lock:
            if _model_bundle is None:  # double-checked locking
                logger.info("Loading model bundle...")
                _model_bundle = ModelBundle()
                logger.info("Model loaded successfully")
    return _model_bundle


def require_model_bundle() -> ModelBundle:
    try:
        return get_model_bundle()
    except Exception as exc:
        logger.exception("Model loading failed")
        raise HTTPException(status_code=500, detail="Model not loaded") from exc