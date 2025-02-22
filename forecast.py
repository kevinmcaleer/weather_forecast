from influxdb import InfluxDBClient
import pandas as pd
import json
from time import sleep
import paho.mqtt.client as mqtt
from statsmodels.tsa.arima.model import ARIMA

# Setup MQTT Connection
MQTT_HOST = "192.168.1.152"
MQTT_PORT = 1883

# Use modern callback API and MQTT v3.1.1
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)

# InfluxDB Connection (for InfluxDB 1.x)
INFLUXDB_HOST = "192.168.1.10"
INFLUXDB_PORT = 8086
DATABASE = "weather"

client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=DATABASE)

def get_data():
    """ Get latest weather data from InfluxDB for Summerhouse location """
    # Query hourly mean pressure for the last 24 hours, only by location
    query = """
        SELECT MEAN("pressure") AS "pressure"
        FROM "weather"
        WHERE "location" = 'Summerhouse'
        AND time > now() - 24h
        GROUP BY time(1h)
        ORDER BY time ASC
    """
    result = client.query(query)
    
    data = list(result.get_points())
    if not data:
        raise ValueError("No data returned for Summerhouse location in the last 24 hours")
    
    # Debug: Print raw data points
    print("Raw data (first 5 points):", data[:5])
    
    df = pd.DataFrame(data)
    
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    df = df.sort_index()
    
    # Round pressure values to 1 decimal point
    df["pressure"] = df["pressure"].round(1)
    
    # Debug: Print length of data
    print(f"Number of hourly points: {len(df)}")
    
    # Get the last 24 hourly pressure values as a list
    last_24_pressures = df["pressure"].tail(24).tolist()
    
    # Ensure we have enough data for ARIMA (at least 6 points for order=(2,1,0))
    if len(df) < 6:
        raise ValueError("Not enough valid pressure data points for ARIMA model")
    
    # Use a simpler ARIMA model to reduce non-stationarity issues
    model = ARIMA(df['pressure'], order=(2,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=3)
    
    current_pressure = df["pressure"].iloc[-1]
    predicted_pressure = round(forecast.iloc[-1], 1)  # Round the forecast too
    
    return current_pressure, predicted_pressure, last_24_pressures

def interpret_weather(current, future):
    change = future - current
    if change > 3:
        return "Fair weather expected, skies clearing."
    elif 1 <= change <= 3:
        return "Weather improving, light clouds."
    elif -1 <= change <= 1:
        return "Stable conditions, no major change expected."
    elif -3 <= change < -1:
        return "Clouds increasing, possible rain."
    else:
        return "Storm approaching, prepare for bad weather."

while True:
    print("waking up")
    try:
        current_pressure, predicted_pressure, last_24_pressures = get_data()
        prediction = interpret_weather(current_pressure, predicted_pressure)
        
        # Publish pressure readings to MQTT
        print(f"last_24_pressures: {last_24_pressures}")
        pressure_payload = json.dumps({"last_24_pressures": last_24_pressures})
        
        mqtt_client.connect(MQTT_HOST, MQTT_PORT)
        mqtt_client.publish("weather/prediction", prediction)
        mqtt_client.publish("weather/pressure", pressure_payload)
        mqtt_client.disconnect()
        
        print("Sleeping for 5 seconds")
        sleep(5)
    except ValueError as e:
        print(f"Error: {e}")
        print("Sleeping for 5 seconds before retrying")
        sleep(5)