// ============================================================
// SMART PLANT CLOUD DASHBOARD
// ============================================================


// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";

const DEVICE_ID = "PLANT-001";


// Dashboard refresh interval

const REFRESH_INTERVAL = 3000;


// Automatic watering state

let automaticWatering = false;


// Chart objects

let moistureChart = null;

let temperatureChart = null;

let humidityChart = null;


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Smart Plant Dashboard started.");

    loadDashboard();

    setInterval(loadDashboard, REFRESH_INTERVAL);

});


// ============================================================
// LOAD COMPLETE DASHBOARD
// ============================================================

async function loadDashboard() {

    try {

        await loadLatestReading();

        await loadHistory();

        await loadAlerts();

        await loadWateringHistory();

        updateConnectionStatus(true);

        updateLastUpdate();

    }

    catch (error) {

        console.error(
            "Dashboard loading error:",
            error
        );

        updateConnectionStatus(false);

    }

}


// ============================================================
// LOAD LATEST SENSOR READING
// ============================================================

async function loadLatestReading() {

    const response = await fetch(

        `${API_BASE_URL}/api/devices/${DEVICE_ID}/latest`

    );


    if (!response.ok) {

        throw new Error(
            "Latest sensor data unavailable"
        );

    }


    const data = await response.json();


    console.log(
        "Latest reading:",
        data
    );


    // Soil moisture

    document.getElementById(
        "soilMoisture"
    ).textContent =
        `${Number(data.soil_moisture).toFixed(1)}%`;


    // Temperature

    document.getElementById(
        "temperature"
    ).textContent =
        `${Number(data.temperature).toFixed(1)}°C`;


    // Humidity

    document.getElementById(
        "humidity"
    ).textContent =
        `${Number(data.humidity).toFixed(1)}%`;


    // Light

    document.getElementById(
        "light"
    ).textContent =
        `${Number(data.light_level).toFixed(1)}%`;


    // Plant status

    updatePlantStatus(
        Number(data.soil_moisture)
    );


    // Device status

    document.getElementById(
        "deviceStatus"
    ).textContent = "ONLINE";

}


// ============================================================
// PLANT STATUS
// ============================================================

function updatePlantStatus(moisture) {

    const statusElement =
        document.getElementById("plantStatus");


    const messageElement =
        document.getElementById("moistureMessage");


    if (moisture < 20) {

        statusElement.textContent =
            "Critical";

        statusElement.className =
            "status critical";


        messageElement.textContent =
            "Very dry - watering required";

    }

    else if (moisture < 30) {

        statusElement.textContent =
            "Needs Water";

        statusElement.className =
            "status warning";


        messageElement.textContent =
            "Moisture below threshold";

    }

    else {

        statusElement.textContent =
            "Healthy";

        statusElement.className =
            "status healthy";


        messageElement.textContent =
            "Moisture level is healthy";

    }

}


// ============================================================
// LOAD HISTORY
// ============================================================

async function loadHistory() {

    try {

        const response = await fetch(

            `${API_BASE_URL}/api/devices/${DEVICE_ID}/history`

        );


        if (!response.ok) {

            throw new Error(
                "History unavailable"
            );

        }


        const data = await response.json();


        console.log(
            "History:",
            data
        );


        if (
            !data.readings ||
            data.readings.length === 0
        ) {

            console.log(
                "No historical readings."
            );

            return;

        }


        // API returns newest first.
        // Reverse so chart displays oldest -> newest.

        const readings =
            [...data.readings].reverse();


        const labels =
            readings.map(
                reading =>
                    formatTime(
                        reading.timestamp
                    )
            );


        const moisture =
            readings.map(
                reading =>
                    Number(
                        reading.soil_moisture
                    )
            );


        const temperature =
            readings.map(
                reading =>
                    Number(
                        reading.temperature
                    )
            );


        const humidity =
            readings.map(
                reading =>
                    Number(
                        reading.humidity
                    )
            );


        createMoistureChart(
            labels,
            moisture
        );


        createTemperatureChart(
            labels,
            temperature
        );


        createHumidityChart(
            labels,
            humidity
        );

    }

    catch (error) {

        console.error(
            "History error:",
            error
        );

    }

}


// ============================================================
// MOISTURE CHART
// ============================================================

function createMoistureChart(
    labels,
    values
) {

    const canvas =
        document.getElementById(
            "moistureChart"
        );


    if (moistureChart) {

        moistureChart.destroy();

    }


    moistureChart =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Soil Moisture (%)",

                            data: values,

                            borderWidth: 2,

                            tension: 0.3,

                            fill: false

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        y: {

                            beginAtZero: true,

                            max: 100

                        }

                    }

                }

            }
        );

}


// ============================================================
// TEMPERATURE CHART
// ============================================================

function createTemperatureChart(
    labels,
    values
) {

    const canvas =
        document.getElementById(
            "temperatureChart"
        );


    if (temperatureChart) {

        temperatureChart.destroy();

    }


    temperatureChart =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Temperature (°C)",

                            data: values,

                            borderWidth: 2,

                            tension: 0.3,

                            fill: false

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false

                }

            }
        );

}


// ============================================================
// HUMIDITY CHART
// ============================================================

function createHumidityChart(
    labels,
    values
) {

    const canvas =
        document.getElementById(
            "humidityChart"
        );


    if (humidityChart) {

        humidityChart.destroy();

    }


    humidityChart =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Humidity (%)",

                            data: values,

                            borderWidth: 2,

                            tension: 0.3,

                            fill: false

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false

                }

            }
        );

}


// ============================================================
// MANUAL WATERING
// ============================================================

async function manualWater() {

    const message =
        document.getElementById(
            "manualWaterMessage"
        );


    message.textContent =
        "Starting virtual pump...";


    try {

        const response = await fetch(

            `${API_BASE_URL}/api/devices/${DEVICE_ID}/water`,

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                }

            }

        );


        const data =
            await response.json();


        console.log(
            "Manual watering response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Watering failed"
            );

        }


        message.textContent =
            "💧 Virtual pump activated successfully!";


        setTimeout(

            () => {

                message.textContent = "";

            },

            5000

        );


        await loadDashboard();

    }

    catch (error) {

        console.error(
            "Manual watering error:",
            error
        );


        message.textContent =
            `❌ ${error.message}`;

    }

}


// ============================================================
// AUTOMATIC WATERING TOGGLE
// ============================================================

function toggleAutomaticWatering() {

    automaticWatering =
        !automaticWatering;


    const button =
        document.getElementById(
            "autoWaterButton"
        );


    const status =
        document.getElementById(
            "autoWaterStatus"
        );


    if (automaticWatering) {

        button.textContent =
            "Disable Auto Water";


        status.textContent =
            "Automatic watering is ON";

    }

    else {

        button.textContent =
            "Enable Auto Water";


        status.textContent =
            "Automatic watering is OFF";

    }

}


// ============================================================
// UPDATE THRESHOLD
// ============================================================

async function updateThreshold() {

    const input =
        document.getElementById(
            "thresholdInput"
        );


    const message =
        document.getElementById(
            "thresholdMessage"
        );


    const threshold =
        Number(input.value);


    if (
        threshold < 5 ||
        threshold > 95
    ) {

        message.textContent =
            "Threshold must be between 5% and 95%.";

        return;

    }


    try {

        const response = await fetch(

            `${API_BASE_URL}/api/devices/${DEVICE_ID}/threshold`,

            {

                method: "PUT",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    threshold:
                        threshold

                })

            }

        );


        const data =
            await response.json();


        console.log(
            "Threshold response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Threshold update failed"
            );

        }


        message.textContent =
            `Threshold saved at ${threshold}%`;

    }

    catch (error) {

        console.error(
            "Threshold error:",
            error
        );


        message.textContent =
            `❌ ${error.message}`;

    }

}


// ============================================================
// LOAD ALERTS
// ============================================================

async function loadAlerts() {

    const container =
        document.getElementById(
            "alertsContainer"
        );


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/alerts`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load alerts"
            );

        }


        const data =
            await response.json();


        console.log(
            "Alerts:",
            data
        );


        if (
            !data.alerts ||
            data.alerts.length === 0
        ) {

            container.innerHTML =
                "<p>No alerts.</p>";

            return;

        }


        container.innerHTML = "";


        data.alerts.forEach(
            alert => {

                const div =
                    document.createElement(
                        "div"
                    );


                div.className =
                    `alert ${
                        String(
                            alert.alert_type ||
                            "info"
                        ).toLowerCase()
                    }`;


                div.innerHTML = `

                    <div class="alert-title">

                        ${alert.alert_type || "Alert"}

                    </div>

                    <div>

                        ${alert.message || ""}

                    </div>

                    <div class="alert-time">

                        ${formatDateTime(
                            alert.created_at
                        )}

                    </div>

                `;


                container.appendChild(div);

            }
        );

    }

    catch (error) {

        console.error(
            "Alerts error:",
            error
        );


        container.innerHTML =
            "<p>Unable to load alerts.</p>";

    }

}


// ============================================================
// LOAD WATERING HISTORY
// ============================================================

async function loadWateringHistory() {

    const container =
        document.getElementById(
            "wateringHistory"
        );


    try {

        const response =
            await fetch(

                `${API_BASE_URL}/api/devices/${DEVICE_ID}/watering-history`

            );


        if (!response.ok) {

            throw new Error(
                "Watering history unavailable"
            );

        }


        const data =
            await response.json();


        console.log(
            "Watering history:",
            data
        );


        const events =
            data.events ||
            data.watering_events ||
            [];


        if (events.length === 0) {

            container.innerHTML =
                "<p>No watering events yet.</p>";

            return;

        }


        container.innerHTML = "";


        events.forEach(
            event => {

                const div =
                    document.createElement(
                        "div"
                    );


                div.className =
                    "watering-event";


                div.innerHTML = `

                    <strong>
                        💧 ${
                            event.trigger_type ||
                            "Watering"
                        }
                    </strong>

                    <span>
                        Moisture before:
                        ${
                            event.moisture_before ??
                            "--"
                        }%
                    </span>

                    <br>

                    <span>
                        Duration:
                        ${
                            event.duration ??
                            "--"
                        } seconds
                    </span>

                    <br>

                    <small>
                        ${
                            formatDateTime(
                                event.timestamp
                            )
                        }
                    </small>

                `;


                container.appendChild(div);

            }
        );

    }

    catch (error) {

        console.error(
            "Watering history error:",
            error
        );


        container.innerHTML =
            "<p>Unable to load watering history.</p>";

    }

}


// ============================================================
// CONNECTION STATUS
// ============================================================

function updateConnectionStatus(
    connected
) {

    const dot =
        document.getElementById(
            "connectionDot"
        );


    const text =
        document.getElementById(
            "connectionText"
        );


    if (connected) {

        dot.style.color =
            "#22c55e";


        text.textContent =
            "Cloud API Connected";

    }

    else {

        dot.style.color =
            "#ef4444";


        text.textContent =
            "Backend Offline";

        document.getElementById(
            "deviceStatus"
        ).textContent =
            "OFFLINE";

    }

}


// ============================================================
// LAST UPDATE
// ============================================================

function updateLastUpdate() {

    document.getElementById(
        "lastUpdate"
    ).textContent =
        new Date().toLocaleTimeString();

}


// ============================================================
// TIME FORMATTING
// ============================================================

function formatTime(timestamp) {

    if (!timestamp) {

        return "";

    }


    return new Date(
        timestamp
    ).toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }
    );

}


// ============================================================
// DATE + TIME
// ============================================================

function formatDateTime(timestamp) {

    if (!timestamp) {

        return "";

    }


    return new Date(
        timestamp
    ).toLocaleString();

}