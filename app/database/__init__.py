from app.database.base import Base
from app.database.connection import engine
from sqlalchemy import inspect, text


def init_db() -> None:
    # Import models before metadata creation so SQLAlchemy sees tables.
    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _apply_lightweight_migrations()


def _apply_lightweight_migrations() -> None:
    inspector = inspect(engine)
    if "scoring_logs" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("scoring_logs")}
    if "model_version" not in columns:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE scoring_logs ADD COLUMN model_version VARCHAR(255) DEFAULT 'unknown'"
                )
            )

