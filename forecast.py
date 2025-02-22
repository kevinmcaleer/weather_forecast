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

def get_pressure_data():
    """ Get latest pressure data from InfluxDB for Summerhouse location """
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
    
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    df = df.sort_index()
    
    df["pressure"] = df["pressure"].round(1)
    
     # Ensure we have enough data for ARIMA (at least 6 points for order=(2,1,0))
    if len(df) < 6:
        raise ValueError("Not enough valid pressure data points for ARIMA model")
    
    # Use a simpler ARIMA model to reduce non-stationarity issues
    model = ARIMA(df['pressure'], order=(2,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=3)
    predicted_pressure = round(forecast.iloc[-1], 1)

    last_24_pressures = df["pressure"].tail(24).tolist()
    current_pressure = df["pressure"].iloc[-1]
    
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

def get_temperature_data():
    """ Get latest temperature data from InfluxDB for RobotLab location """
    query = """
        SELECT MEAN("temperature") AS "temperature"
        FROM "weather"
        WHERE "location" = 'RobotLab'
        AND time > now() - 24h
        GROUP BY time(1h)
        ORDER BY time ASC
    """
    result = client.query(query)
    
    data = list(result.get_points())
    if not data:
        raise ValueError("No data returned for RobotLab location in the last 24 hours")
    
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    df = df.sort_index()
    
    df["temperature"] = df["temperature"].round(1)
    
    last_24_temperatures = df["temperature"].tail(24).tolist()
    current_temperature = df["temperature"].iloc[-1]
    
    return current_temperature, last_24_temperatures

while True:
    print("Waking up")
    try:
        current_pressure, predicted_pressure, last_24_pressures = get_pressure_data()
        current_temperature, last_24_temperatures = get_temperature_data()
        
        prediction = interpret_weather(current_pressure, predicted_pressure)
        print(f"Predicted weather: {prediction}")

        pressure_payload = json.dumps({"last_24_pressures": last_24_pressures})
        temperature_payload = json.dumps({"last_24_temperatures": last_24_temperatures})
        current_pressure_payload = json.dumps({"current_pressure": current_pressure})
        current_temperature_payload = json.dumps({"current_temperature": current_temperature})
        
        print("Publishing pressure and temperature data to MQTT")
        print("Pressure:", pressure_payload)
        print("Temperature:", temperature_payload)
        print("Current Pressure:", current_pressure_payload)
        print("Current Temperature:", current_temperature_payload)

        mqtt_client.connect(MQTT_HOST, MQTT_PORT)
        mqtt_client.publish("weather/pressure", pressure_payload)
        mqtt_client.publish("weather/current_pressure", current_pressure_payload)
        mqtt_client.publish("weather/temperature", temperature_payload)
        mqtt_client.publish("weather/current_temperature", current_temperature_payload)
        mqtt_client.publish("weather/prediction", prediction)
        mqtt_client.disconnect()
        
        print("Sleeping for 5 seconds")
        sleep(5)
    except ValueError as e:
        print(f"Error: {e}")
        print("Sleeping for 5 seconds before retrying")
        sleep(5)
