from influxdb import InfluxDBClient
import pandas as pd
import json
from time import sleep
import paho.mqtt.client as mqtt
from statsmodels.tsa.arima.model import ARIMA

# Setup MQTT Connection
MQTT_HOST = "192.168.1.152"
MQTT_PORT = 1883

mqtt_client = mqtt.Client()

# InfluxDB Connection (for InfluxDB 1.x)
INFLUXDB_HOST = "192.168.1.10"
INFLUXDB_PORT = 8086
DATABASE = "weather"

client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=DATABASE)

def get_data():
    """ Get latest weather data from InfluxDB """
    query = "SELECT * FROM weather WHERE time > now() - 24h"
    result = client.query(query)
    
    data = list(result.get_points())
    df = pd.DataFrame(data)
    
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    df = df.sort_index()
    
    # Round pressure values to 1 decimal point
    df["pressure"] = df["pressure"].round(1)
    
    # Get the last 20 pressure values as a list
    last_20_pressures = df["pressure"].tail(20).tolist()
    
    model = ARIMA(df['pressure'], order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=3)
    
    current_pressure = df["pressure"].iloc[-1]
    predicted_pressure = round(forecast.iloc[-1], 1)  # Round the forecast too
    
    return current_pressure, predicted_pressure, last_20_pressures

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
    current_pressure, predicted_pressure, last_20_pressures = get_data()
    prediction = interpret_weather(current_pressure, predicted_pressure)
    
    # Publish pressure readings to MQTT
    print(f"last_20_pressures: {last_20_pressures}")
    pressure_payload = json.dumps({"last_20_pressures": last_20_pressures})
    
    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.publish("weather/prediction", prediction)
    mqtt_client.publish("weather/pressure", pressure_payload)
    mqtt_client.disconnect()
    
    print("Sleeping for 5 seconds")
    sleep(5)