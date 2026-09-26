# automation/plant_profiles.py


PLANT_PROFILES = {

    "tomato": {
        "name": "Tomato Plant",
        "moisture_threshold": 30,
        "description": "Tomato plants require moderate soil moisture."
    },

    "chilli": {
        "name": "Chilli Plant",
        "moisture_threshold": 35,
        "description": "Chilli plants prefer consistently moist soil."
    },

    "cucumber": {
        "name": "Cucumber Plant",
        "moisture_threshold": 40,
        "description": "Cucumber plants require relatively high soil moisture."
    },

    "basil": {
        "name": "Basil Plant",
        "moisture_threshold": 35,
        "description": "Basil requires regular watering and moderately moist soil."
    },

    "mint": {
        "name": "Mint Plant",
        "moisture_threshold": 40,
        "description": "Mint prefers consistently moist soil."
    }
}


def get_plant_profile(plant_type):

    plant_type = plant_type.lower().strip()

    if plant_type not in PLANT_PROFILES:
        raise ValueError(
            f"Unknown plant type: {plant_type}"
        )

    return PLANT_PROFILES[plant_type]


def get_all_plant_profiles():

    return PLANT_PROFILES