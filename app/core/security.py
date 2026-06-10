from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if settings.API_KEY is None:
        raise HTTPException(
            status_code=500,
            detail="API key not configured on server",
        )

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API Key",
        )

    return api_key