from pydantic import BaseModel, Field


class ShockConfig(BaseModel):
    type: str
    start_step: int | None = None
    duration: int | None = None
    severity: float | None = None
    erosion: float | None = None
    step: int | None = None
    vol_spike: float | None = None


class SimulationRequest(BaseModel):
    borrower_data: dict
    shock: ShockConfig | None = None
    n_sims: int = Field(default=10000, ge=100, le=100000)
    T: float = Field(default=2.0, gt=0)
    n_steps: int = Field(default=24, ge=1, le=240)
