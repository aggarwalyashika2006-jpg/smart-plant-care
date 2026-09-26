API_URL = "http://127.0.0.1:8000/api/sensors/data"

DEVICE_ID = "PLANT-001"

# How often the simulator sends data
SEND_INTERVAL = 5

# Starting sensor values
INITIAL_SOIL_MOISTURE = 55.0
INITIAL_TEMPERATURE = 28.0
INITIAL_HUMIDITY = 65.0
INITIAL_LIGHT = 70.0

# Soil moisture behaviour
MOISTURE_DECREASE = 1.5
MOISTURE_INCREASE_AFTER_WATERING = 5.0

# Safety limits
MIN_SOIL_MOISTURE = 0.0
MAX_SOIL_MOISTURE = 100.0