import random
import time
import logging
from datetime import datetime

import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000/api/sensors/data"

DEVICE_ID = "PLANT-001"

SEND_INTERVAL = 3

REQUEST_TIMEOUT = 5

MOISTURE_START = 55.0

MOISTURE_DECREASE = 0.8

MOISTURE_INCREASE_AFTER_WATERING = 5.0


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(

    level=logging.INFO,

    format=
        "%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


# ============================================================
# SENSOR STATE
# ============================================================

soil_moisture = MOISTURE_START

temperature = 28.0

humidity = 60.0

light_level = 50.0


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value,
    minimum,
    maximum
):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ============================================================
# SIMULATE SOIL MOISTURE
# ============================================================

def update_soil_moisture():

    global soil_moisture

    # Normally plants slowly lose moisture.

    soil_moisture -= (
        MOISTURE_DECREASE
        + random.uniform(
            -0.2,
            0.2
        )
    )


    soil_moisture = clamp(
        soil_moisture,
        0,
        100
    )


# ============================================================
# SIMULATE TEMPERATURE
# ============================================================

def update_temperature():

    global temperature

    # Small gradual temperature change.

    change = random.uniform(
        -0.5,
        0.5
    )

    temperature += change

    temperature = clamp(
        temperature,
        20,
        35
    )


# ============================================================
# SIMULATE HUMIDITY
# ============================================================

def update_humidity():

    global humidity

    change = random.uniform(
        -1.5,
        1.5
    )

    humidity += change

    humidity = clamp(
        humidity,
        40,
        85
    )


# ============================================================
# SIMULATE LIGHT
# ============================================================

def update_light():

    global light_level

    change = random.uniform(
        -5,
        5
    )

    light_level += change

    light_level = clamp(
        light_level,
        0,
        100
    )


# ============================================================
# CREATE SENSOR READING
# ============================================================

def create_reading():

    update_soil_moisture()

    update_temperature()

    update_humidity()

    update_light()


    return {

        "device_id":
            DEVICE_ID,

        "soil_moisture":
            round(
                soil_moisture,
                2
            ),

        "temperature":
            round(
                temperature,
                2
            ),

        "humidity":
            round(
                humidity,
                2
            ),

        "light_level":
            round(
                light_level,
                2
            ),

        "timestamp":
            datetime.utcnow().isoformat()

    }


# ============================================================
# SEND DATA
# ============================================================

def send_reading(
    reading
):

    try:

        response = requests.post(

            API_URL,

            json=reading,

            timeout=REQUEST_TIMEOUT

        )


        if response.status_code == 200:

            logger.info(

                "Sensor data sent successfully | "
                "Moisture: %.2f%% | "
                "Temperature: %.2f°C | "
                "Humidity: %.2f%% | "
                "Light: %.2f%%",

                reading["soil_moisture"],

                reading["temperature"],

                reading["humidity"],

                reading["light_level"]

            )


            try:

                result =response.json()


                watering =result.get(
                        "watering",
                        {}
                    )


                logger.info(

                    "Watering decision: %s | "
                    "Pump: %s | "
                    "Reason: %s",

                    watering.get(
                        "watering_required"
                    ),

                    watering.get(
                        "pump_status"
                    ),

                    watering.get(
                        "reason"
                    )

                )

            except Exception:

                pass


            return True


        else:

            logger.error(

                "API returned status %s: %s",

                response.status_code,

                response.text

            )

            return False


    except requests.exceptions.RequestException as error:

        logger.error(

            "Could not connect to backend: %s",

            error

        )

        return False


# ============================================================
# MAIN SIMULATOR
# ============================================================

def main():

    logger.info(
        "=========================================="
    )

    logger.info(
        "SMART PLANT SENSOR SIMULATOR"
    )

    logger.info(
        "=========================================="
    )

    logger.info(
        "Device ID: %s",
        DEVICE_ID
    )

    logger.info(
        "API: %s",
        API_URL
    )

    logger.info(
        "Starting moisture: %.2f%%",
        soil_moisture
    )

    logger.info(
        "Sending interval: %s seconds",
        SEND_INTERVAL
    )

    logger.info(
        "Press CTRL+C to stop."
    )


    while True:

        try:

            reading =create_reading()


            send_reading(
                reading
            )


            time.sleep(
                SEND_INTERVAL
            )


        except KeyboardInterrupt:

            logger.info(
                "Simulator stopped."
            )

            break


        except Exception as error:

            logger.exception(
                "Unexpected simulator error: %s",
                error
            )

            time.sleep(
                SEND_INTERVAL
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()