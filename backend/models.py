from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

from .database import Base


# =========================================================
# SENSOR READING
# =========================================================

class SensorReading(Base):

    __tablename__ = "sensor_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    device_id = Column(
        String,
        index=True,
        nullable=False
    )

    soil_moisture = Column(
        Float,
        nullable=False
    )

    temperature = Column(
        Float,
        nullable=False
    )

    humidity = Column(
        Float,
        nullable=False
    )

    light_level = Column(
        Float,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# =========================================================
# WATERING EVENT
# =========================================================

class WateringEvent(Base):

    __tablename__ = "watering_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    device_id = Column(
        String,
        index=True,
        nullable=False
    )

    plant = Column(
        String,
        nullable=False
    )

    mode = Column(
        String,
        nullable=False
    )

    reason = Column(
        String,
        nullable=False
    )

    duration = Column(
        Float,
        default=0,
        nullable=False
    )

    moisture_before = Column(
        Float,
        nullable=True
    )

    moisture_after = Column(
        Float,
        nullable=True
    )

    status = Column(
        String,
        nullable=False
    )

    started_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ended_at = Column(
        DateTime,
        nullable=True
    )