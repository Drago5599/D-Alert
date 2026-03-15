from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class AlertBase(SQLModel):
    source: str  # social, weather
    raw_text: str
    disaster_type: str
    severity: int = Field(default=1)  # 1-3
    confidence: float = Field(default=0.5)  # 0-1
    lat: Optional[float] = None
    lon: Optional[float] = None
    location_name: Optional[str] = None
    timestamp_utc: datetime = Field(default_factory=datetime.utcnow)
    risk_score: float = Field(default=0.0)
    cluster_id: Optional[str] = None
    status: str = Field(default="new")  # new, acknowledged, resolved
    suggested_action: Optional[str] = None

class Alert(AlertBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class AlertCreate(AlertBase):
    pass

class AlertRead(AlertBase):
    id: uuid.UUID
