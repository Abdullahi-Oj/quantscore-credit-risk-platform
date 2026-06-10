from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ScoringLog(Base):
    __tablename__ = "scoring_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    endpoint: Mapped[str] = mapped_column(String(64))
    probability: Mapped[float] = mapped_column(Float)
    risk_category: Mapped[str] = mapped_column(String(32))
    model_version: Mapped[str] = mapped_column(
        String(255), default="unknown"
    )
    client_ip: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
