from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models
from .schemas import SensorData

from automation.watering_engine import WateringEngine
from automation.plant_profiles import (
    get_plant_profile,
    get_all_plant_profiles
)


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Cloud Connected Smart Plant Care",
    description="Smart plant monitoring and virtual watering system",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# PLANT CONFIGURATION
# =========================================================

CURRENT_PLANT = "tomato"

plant_profile = get_plant_profile(
    CURRENT_PLANT
)


# =========================================================
# WATERING ENGINE
# =========================================================

watering_engine = WateringEngine(
    moisture_threshold=
        plant_profile["moisture_threshold"],

    minimum_water_tank=10,

    cooldown_minutes=0,

    maximum_watering_duration=30
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message":
            "Smart Plant Cloud System is running!",

        "status":
            "success",

        "plant":
            plant_profile["name"],

        "moisture_threshold":
            watering_engine.moisture_threshold
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "database": "connected"
    }


# =========================================================
# CURRENT PLANT
# =========================================================

@app.get("/api/plant")
def get_current_plant():

    return {

        "plant_type":
            CURRENT_PLANT,

        "plant_name":
            plant_profile["name"],

        "moisture_threshold":
            watering_engine.moisture_threshold,

        "description":
            plant_profile["description"]
    }


# =========================================================
# ALL PLANTS
# =========================================================

@app.get("/api/plants")
def get_plants():

    return get_all_plant_profiles()


# =========================================================
# CHANGE PLANT
# =========================================================

@app.post("/api/plant/{plant_type}")
def change_plant(
    plant_type: str
):

    global CURRENT_PLANT
    global plant_profile

    try:

        profile = get_plant_profile(
            plant_type
        )

    except Exception:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Plant profile "
                f"'{plant_type}' not found."
            )
        )

    CURRENT_PLANT = (
        plant_type.lower()
    )

    plant_profile = profile

    watering_engine.set_moisture_threshold(
        profile["moisture_threshold"]
    )

    return {

        "success": True,

        "plant_type":
            CURRENT_PLANT,

        "plant_name":
            profile["name"],

        "moisture_threshold":
            watering_engine.moisture_threshold,

        "description":
            profile["description"]
    }


# =========================================================
# RECEIVE SENSOR DATA
# =========================================================

@app.post("/api/sensors/data")
def receive_sensor_data(
    data: SensorData,
    db: Session = Depends(get_db)
):

    print("")
    print(
        "========================================"
    )
    print(
        "RECEIVING SENSOR DATA"
    )
    print(
        "========================================"
    )

    print(
        "Device:",
        data.device_id
    )

    print(
        "Plant:",
        plant_profile["name"]
    )

    print(
        "Moisture:",
        data.soil_moisture
    )

    print(
        "Temperature:",
        data.temperature
    )

    print(
        "Humidity:",
        data.humidity
    )

    print(
        "Light:",
        data.light_level
    )

    try:

        # -------------------------------------------------
        # AUTOMATIC WATERING
        # -------------------------------------------------

        watering_result = (
            watering_engine.process_reading(
                soil_moisture=
                    data.soil_moisture,

                water_tank_level=100
            )
        )

        print(
            "Watering result:"
        )

        print(
            watering_result
        )

        # -------------------------------------------------
        # SAVE SENSOR READING
        # -------------------------------------------------

        reading = models.SensorReading(

            device_id=
                data.device_id,

            soil_moisture=
                data.soil_moisture,

            temperature=
                data.temperature,

            humidity=
                data.humidity,

            light_level=
                data.light_level,

            timestamp=
                data.timestamp
        )

        db.add(reading)

        db.commit()

        db.refresh(reading)

        # -------------------------------------------------
        # AUTOMATIC WATERING EVENT
        # -------------------------------------------------

        if (
            watering_result.get(
                "watering_required"
            )
            and
            watering_result.get(
                "pump_status"
            ) == "ON"
        ):

            existing_event = (
                db.query(
                    models.WateringEvent
                )
                .filter(
                    models.WateringEvent.device_id
                    == data.device_id
                )
                .filter(
                    models.WateringEvent.status
                    == "IN_PROGRESS"
                )
                .first()
            )

            if existing_event is None:

                watering_event = (
                    models.WateringEvent(

                        device_id=
                            data.device_id,

                        plant=
                            plant_profile["name"],

                        mode=
                            "AUTOMATIC",

                        reason=
                            watering_result[
                                "reason"
                            ],

                        duration=0,

                        moisture_before=
                            data.soil_moisture,

                        moisture_after=None,

                        status=
                            "IN_PROGRESS",

                        started_at=
                            data.timestamp
                    )
                )

                db.add(
                    watering_event
                )

                db.commit()

        # -------------------------------------------------
        # COMPLETE AUTOMATIC EVENT
        # -------------------------------------------------

        if (
            watering_result.get(
                "event_completed"
            )
        ):

            event = (
                db.query(
                    models.WateringEvent
                )
                .filter(
                    models.WateringEvent.device_id
                    == data.device_id
                )
                .filter(
                    models.WateringEvent.status
                    == "IN_PROGRESS"
                )
                .order_by(
                    models.WateringEvent.id.desc()
                )
                .first()
            )

            if event is not None:

                event.status = "COMPLETED"

                event.ended_at = (
                    data.timestamp
                )

                event.moisture_after = (
                    data.soil_moisture
                )

                if event.started_at:

                    duration = (
                        event.ended_at -
                        event.started_at
                    )

                    event.duration = (
                        duration.total_seconds()
                    )

                db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "message":
                "Sensor data received successfully",

            "reading_id":
                reading.id,

            "device_id":
                reading.device_id,

            "plant":
                plant_profile["name"],

            "soil_moisture":
                reading.soil_moisture,

            "temperature":
                reading.temperature,

            "humidity":
                reading.humidity,

            "light_level":
                reading.light_level,

            "timestamp":
                reading.timestamp,

            "watering":
                watering_result
        }

    except Exception as error:

        db.rollback()

        print("")
        print(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )
        print(
            "ERROR PROCESSING SENSOR DATA"
        )
        print(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )

        print(
            str(error)
        )

        print(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )
        print("")

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to process sensor data: "
                f"{str(error)}"
            )
        )


# =========================================================
# LATEST SENSOR READING
# =========================================================

@app.get(
    "/api/devices/{device_id}/latest"
)
def get_latest_sensor_reading(
    device_id: str,
    db: Session = Depends(get_db)
):

    reading = (

        db.query(
            models.SensorReading
        )

        .filter(
            models.SensorReading.device_id
            == device_id
        )

        .order_by(
            models.SensorReading.timestamp.desc()
        )

        .first()
    )

    if reading is None:

        raise HTTPException(
            status_code=404,
            detail="No sensor data found"
        )

    return {

        "id":
            reading.id,

        "device_id":
            reading.device_id,

        "soil_moisture":
            reading.soil_moisture,

        "temperature":
            reading.temperature,

        "humidity":
            reading.humidity,

        "light_level":
            reading.light_level,

        "timestamp":
            reading.timestamp
    }


# =========================================================
# SENSOR HISTORY
# =========================================================

@app.get(
    "/api/devices/{device_id}/history"
)
def get_sensor_history(
    device_id: str,
    db: Session = Depends(get_db)
):

    readings = (

        db.query(
            models.SensorReading
        )

        .filter(
            models.SensorReading.device_id
            == device_id
        )

        .order_by(
            models.SensorReading.timestamp.desc()
        )

        .limit(100)

        .all()
    )

    return {

        "device_id":
            device_id,

        "count":
            len(readings),

        "readings": [

            {

                "id":
                    reading.id,

                "soil_moisture":
                    reading.soil_moisture,

                "temperature":
                    reading.temperature,

                "humidity":
                    reading.humidity,

                "light_level":
                    reading.light_level,

                "timestamp":
                    reading.timestamp
            }

            for reading in readings
        ]
    }


# =========================================================
# PUMP STATUS
# =========================================================

@app.get(
    "/api/devices/{device_id}/pump"
)
def get_pump_status(
    device_id: str
):

    return {

        "device_id":
            device_id,

        "pump_status":
            (
                "ON"
                if watering_engine.pump_on
                else "OFF"
            ),

        "pump_on":
            watering_engine.pump_on
    }


# =========================================================
# MANUAL WATERING
# =========================================================

@app.post(
    "/api/devices/{device_id}/water"
)
def manual_water(
    device_id: str,
    db: Session = Depends(get_db)
):

    try:

        if watering_engine.pump_on:

            return {

                "device_id":
                    device_id,

                "success":
                    False,

                "pump_status":
                    "ON",

                "message":
                    "Pump is already running."
            }

        started = watering_engine.start_pump(

            mode="MANUAL",

            reason="Manual watering requested",

            moisture_before=None
        )

        if not started:

            return {

                "device_id":
                    device_id,

                "success":
                    False,

                "pump_status":
                    "OFF",

                "message":
                    "Pump could not be started."
            }

        # -------------------------------------------------
        # CREATE MANUAL WATERING EVENT
        # -------------------------------------------------

        watering_event = (
            models.WateringEvent(

                device_id=
                    device_id,

                plant=
                    plant_profile["name"],

                mode=
                    "MANUAL",

                reason=
                    "Manual watering requested",

                duration=0,

                moisture_before=None,

                moisture_after=None,

                status=
                    "IN_PROGRESS",

                started_at=
                    datetime.utcnow()
            )
        )

        db.add(
            watering_event
        )

        db.commit()

        return {

            "device_id":
                device_id,

            "success":
                True,

            "pump_status":
                "ON",

            "watering_mode":
                "MANUAL",

            "message":
                "Manual watering started successfully."
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Manual watering failed: "
                f"{str(error)}"
            )
        )


# =========================================================
# STOP PUMP
# =========================================================

@app.post(
    "/api/devices/{device_id}/pump/stop"
)
def stop_pump(
    device_id: str,
    db: Session = Depends(get_db)
):

    try:

        watering_engine.stop_pump()

        # -------------------------------------------------
        # COMPLETE ACTIVE EVENT
        # -------------------------------------------------

        event = (

            db.query(
                models.WateringEvent
            )

            .filter(
                models.WateringEvent.device_id
                == device_id
            )

            .filter(
                models.WateringEvent.status
                == "IN_PROGRESS"
            )

            .order_by(
                models.WateringEvent.id.desc()
            )

            .first()
        )

        if event is not None:

            event.status = "COMPLETED"

            event.ended_at = (
                datetime.utcnow()
            )

            if event.started_at:

                duration = (
                    event.ended_at -
                    event.started_at
                )

                event.duration = (
                    duration.total_seconds()
                )

            db.commit()

        return {

            "device_id":
                device_id,

            "success":
                True,

            "pump_status":
                "OFF",

            "message":
                "Virtual pump stopped successfully."
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not stop pump: "
                f"{str(error)}"
            )
        )


# =========================================================
# WATERING HISTORY
# =========================================================

@app.get(
    "/api/devices/{device_id}/watering-history"
)
def get_watering_history(
    device_id: str,
    db: Session = Depends(get_db)
):

    events = (

        db.query(
            models.WateringEvent
        )

        .filter(
            models.WateringEvent.device_id
            == device_id
        )

        .order_by(
            models.WateringEvent.started_at.desc()
        )

        .limit(50)

        .all()
    )

    return {

        "device_id":
            device_id,

        "count":
            len(events),

        "events": [

            {

                "id":
                    event.id,

                "plant":
                    event.plant,

                "mode":
                    event.mode,

                "reason":
                    event.reason,

                "duration":
                    event.duration,

                "moisture_before":
                    event.moisture_before,

                "moisture_after":
                    event.moisture_after,

                "status":
                    event.status,

                "started_at":
                    event.started_at,

                "ended_at":
                    event.ended_at
            }

            for event in events
        ]
    }


# =========================================================
# WATERING SETTINGS
# =========================================================

@app.get(
    "/api/watering/settings"
)
def get_watering_settings():

    return {

        "plant":
            plant_profile["name"],

        "settings":
            watering_engine.get_settings()
    }