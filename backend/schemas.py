from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SensorData(BaseModel):

    device_id: str = Field(
        min_length=1,
        max_length=100
    )

    soil_moisture: float = Field(
        ge=0,
        le=100
    )

    temperature: float = Field(
        ge=-20,
        le=60
    )

    humidity: float = Field(
        ge=0,
        le=100
    )

    light_level: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    timestamp: Optional[datetime] = None