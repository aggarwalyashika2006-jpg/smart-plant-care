from watering_engine import WateringEngine


engine = WateringEngine(
    moisture_threshold=30,
    minimum_water_tank=10,
    cooldown_minutes=2,
    maximum_watering_duration=30
)


print("\n--- TEST 1: Healthy Soil ---")

result = engine.process_reading(
    soil_moisture=50,
    water_tank_level=100
)

print(result)


print("\n--- TEST 2: Dry Soil ---")

result = engine.process_reading(
    soil_moisture=25,
    water_tank_level=100
)

print(result)


print("\n--- TEST 3: Watering Continues ---")

result = engine.process_reading(
    soil_moisture=35,
    water_tank_level=100
)

print(result)


print("\n--- TEST 4: Target Reached ---")

result = engine.process_reading(
    soil_moisture=42,
    water_tank_level=100
)

print(result)