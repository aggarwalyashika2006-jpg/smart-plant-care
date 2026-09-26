from datetime import datetime, timedelta


class WateringEngine:

    def __init__(
        self,
        moisture_threshold=30,
        minimum_water_tank=10,
        cooldown_minutes=2,
        maximum_watering_duration=30
    ):

        self.moisture_threshold = moisture_threshold

        self.minimum_water_tank = minimum_water_tank

        self.cooldown_minutes = cooldown_minutes

        self.maximum_watering_duration = (
            maximum_watering_duration
        )

        # -------------------------------------------------
        # PUMP STATE
        # -------------------------------------------------

        self.pump_on = False

        # -------------------------------------------------
        # WATERING TIMING
        # -------------------------------------------------

        self.last_watering_time = None

        self.watering_started_at = None

        # -------------------------------------------------
        # CURRENT WATERING INFORMATION
        # -------------------------------------------------

        self.current_watering_mode = None

        self.current_watering_reason = None

        self.current_moisture_before = None

    # =====================================================
    # SET MOISTURE THRESHOLD
    # =====================================================

    def set_moisture_threshold(self, threshold):

        self.moisture_threshold = threshold

    # =====================================================
    # GET SETTINGS
    # =====================================================

    def get_settings(self):

        return {
            "moisture_threshold":
                self.moisture_threshold,

            "minimum_water_tank":
                self.minimum_water_tank,

            "cooldown_minutes":
                self.cooldown_minutes,

            "maximum_watering_duration":
                self.maximum_watering_duration,

            "pump_on":
                self.pump_on
        }

    # =====================================================
    # CHECK COOLDOWN
    # =====================================================

    def cooldown_completed(self):

        if self.last_watering_time is None:
            return True

        current_time = datetime.utcnow()

        elapsed_time = (
            current_time -
            self.last_watering_time
        )

        return (
            elapsed_time >=
            timedelta(
                minutes=self.cooldown_minutes
            )
        )

    # =====================================================
    # CHECK WHETHER WATERING IS REQUIRED
    # =====================================================

    def should_water(
        self,
        soil_moisture,
        water_tank_level=100
    ):

        print("----------------------------------------")
        print("WATERING ENGINE CHECK")
        print(
            "Soil moisture:",
            soil_moisture
        )
        print(
            "Threshold:",
            self.moisture_threshold
        )
        print(
            "Water tank:",
            water_tank_level
        )
        print(
            "Pump ON:",
            self.pump_on
        )
        print(
            "Cooldown completed:",
            self.cooldown_completed()
        )
        print("----------------------------------------")

        # -------------------------------------------------
        # WATER TANK CHECK
        # -------------------------------------------------

        if (
            water_tank_level <
            self.minimum_water_tank
        ):

            print(
                "Water tank level too low."
            )

            return False

        # -------------------------------------------------
        # PUMP ALREADY ON
        # -------------------------------------------------

        if self.pump_on:

            print(
                "Pump is already ON."
            )

            return False

        # -------------------------------------------------
        # COOLDOWN
        # -------------------------------------------------

        if not self.cooldown_completed():

            print(
                "Watering cooldown is active."
            )

            return False

        # -------------------------------------------------
        # MOISTURE CHECK
        # -------------------------------------------------

        if (
            soil_moisture <
            self.moisture_threshold
        ):

            print(
                "Soil is dry."
            )

            print(
                "Watering is required."
            )

            return True

        print(
            "Soil moisture is sufficient."
        )

        return False

    # =====================================================
    # START PUMP
    # =====================================================

    def start_pump(
        self,
        mode="AUTOMATIC",
        reason="Soil moisture below threshold",
        moisture_before=None
    ):

        if self.pump_on:

            return False

        self.pump_on = True

        self.watering_started_at = (
            datetime.utcnow()
        )

        self.current_watering_mode = mode

        self.current_watering_reason = reason

        self.current_moisture_before = (
            moisture_before
        )

        print("")
        print(
            "========================================"
        )
        print(
            "VIRTUAL PUMP: ON"
        )
        print(
            "Mode:",
            mode
        )
        print(
            "Reason:",
            reason
        )
        print(
            "========================================"
        )
        print("")

        return True

    # =====================================================
    # STOP PUMP
    # =====================================================

    def stop_pump(
        self,
        moisture_after=None
    ):

        if not self.pump_on:

            return False

        self.pump_on = False

        self.last_watering_time = (
            datetime.utcnow()
        )

        self.watering_started_at = None

        self.current_watering_mode = None

        self.current_watering_reason = None

        self.current_moisture_before = None

        print("")
        print(
            "========================================"
        )
        print(
            "VIRTUAL PUMP: OFF"
        )
        print(
            "========================================"
        )
        print("")

        return True

    # =====================================================
    # GET CURRENT WATERING DURATION
    # =====================================================

    def get_current_duration(self):

        if not self.pump_on:

            return 0

        if self.watering_started_at is None:

            return 0

        elapsed = (
            datetime.utcnow() -
            self.watering_started_at
        )

        return elapsed.total_seconds()

    # =====================================================
    # CHECK MAXIMUM DURATION
    # =====================================================

    def maximum_duration_reached(self):

        if not self.pump_on:

            return False

        if self.watering_started_at is None:

            return False

        elapsed_time = (
            datetime.utcnow() -
            self.watering_started_at
        )

        return (
            elapsed_time.total_seconds()
            >=
            self.maximum_watering_duration
        )

    # =====================================================
    # PROCESS SENSOR READING
    # =====================================================

    def process_reading(
        self,
        soil_moisture,
        water_tank_level=100
    ):

        print("")
        print(
            "########################################"
        )
        print(
            "AUTOMATION ENGINE"
        )
        print(
            "########################################"
        )

        result = {
            "watering_required": False,
            "pump_status": "OFF",
            "reason": "",
            "mode": "AUTOMATIC"
        }

        # -------------------------------------------------
        # PUMP CURRENTLY ON
        # -------------------------------------------------

        if self.pump_on:

            result["pump_status"] = "ON"

            stop_threshold = (
                self.moisture_threshold +
                10
            )

            print(
                "Pump is ON."
            )

            print(
                "Stop threshold:",
                stop_threshold
            )

            # -------------------------------------------------
            # TARGET MOISTURE REACHED
            # -------------------------------------------------

            if soil_moisture >= stop_threshold:

                self.stop_pump(
                    moisture_after=soil_moisture
                )

                result["pump_status"] = "OFF"

                result["reason"] = (
                    "Target moisture reached"
                )

                result["event_completed"] = True

                return result

            # -------------------------------------------------
            # SAFETY TIMEOUT
            # -------------------------------------------------

            if self.maximum_duration_reached():

                self.stop_pump(
                    moisture_after=soil_moisture
                )

                result["pump_status"] = "OFF"

                result["reason"] = (
                    "Maximum watering duration reached"
                )

                result["event_completed"] = True

                return result

            # -------------------------------------------------
            # CONTINUE WATERING
            # -------------------------------------------------

            result["reason"] = (
                "Watering in progress"
            )

            result["event_completed"] = False

            return result

        # -------------------------------------------------
        # PUMP CURRENTLY OFF
        # -------------------------------------------------

        if self.should_water(
            soil_moisture,
            water_tank_level
        ):

            self.start_pump(
                mode="AUTOMATIC",
                reason=(
                    "Soil moisture below threshold"
                ),
                moisture_before=soil_moisture
            )

            result["watering_required"] = True

            result["pump_status"] = "ON"

            result["reason"] = (
                "Soil moisture below threshold"
            )

            result["event_completed"] = False

            return result

        # -------------------------------------------------
        # NO WATERING REQUIRED
        # -------------------------------------------------

        result["watering_required"] = False

        result["pump_status"] = "OFF"

        result["reason"] = (
            "No watering required"
        )

        result["event_completed"] = False

        return result