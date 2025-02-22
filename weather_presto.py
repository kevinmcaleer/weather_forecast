from presto import Presto
from umqttsimple import MQTTClient
import network
import gc  # Garbage Collector
from WIFI_CONFIG import SSID, PASSWORD
from time import sleep
import pichart
import json

# Initialize Presto Display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Define Colors
BLUE = display.create_pen(28, 181, 202)
WHITE = display.create_pen(255, 255, 255)

# MQTT Configuration
MQTT_SERVER = "192.168.1.152"
MQTT_PORT = 1883
MQTT_TOPIC = "weather/prediction"
PRESSURE_TOPIC = "weather/pressure"
TEMP_TOPIC = "weather/temperature"
MQTT_CLIENT_ID = "weather"

# Initial pressure list (24 hourly values, default to zeros)
pressure = [0] * 24  # Matches the 24 hourly values from your Python script

temperature = [20,21,20]
# Global variable for prediction text (fixed-size buffer to prevent fragmentation)
prediction = "Waiting for prediction..."[:50]

def sub_cb(topic, msg):
    """ MQTT Subscribe Callback: Updates global variables with received messages. """
    global prediction, pressure, temperature
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    
    if topic == MQTT_TOPIC:  # "weather/prediction"
        print(f'Received MQTT: topic={topic}, msg={msg}')
        prediction = msg[:50]  # Trim to 50 chars to avoid memory issues
    elif topic == PRESSURE_TOPIC:  # "weather/pressure"
        try:
            payload = json.loads(msg)
            # Expecting {"last_24_pressures": [list of 24 values]}
            pressure = payload["last_24_pressures"]
            print(f"Pressure data received: {pressure}")
        except (ValueError, KeyError) as e:
            print(f"Error parsing pressure data: {e}")
    elif topic == TEMP_TOPIC:
        try:
            temp_payload = json.loads(msg)
            # Expecting {"last_24_pressures": [list of 24 values]}
            temperature = temp_payload["last_24_temperatures"]
            print(f"Temperature data received: {temperature}")
        except (ValueError, KeyError) as e:
            print(f"Error parsing Temperature data: {e}")
            

def connect_wifi():
    """ Connect to Wi-Fi. """
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(SSID, PASSWORD)
    
    print("Connecting to Wi-Fi", end="")
    while not sta_if.isconnected():
        print('.', end="")
        sleep(0.5)
    
    print(f'\nConnected to WiFi, IP: {sta_if.ifconfig()[0]}')
    return sta_if

def connect_and_subscribe():
    """ Connect to MQTT broker and subscribe to topics. """
    global MQTT_CLIENT_ID, MQTT_SERVER, TEMP_TOPIC

    print(f"Connecting to MQTT: {MQTT_CLIENT_ID} @ {MQTT_SERVER}:{MQTT_PORT}")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, keepalive=30)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    client.subscribe(PRESSURE_TOPIC)
    client.subscribe(TEMP_TOPIC)
    return client

def restart_reconnect():
    """ Attempt to reconnect to MQTT on failure, cleaning up memory. """
    global client
    
    print('Reconnecting to MQTT...')
    try:
        client.disconnect()  # Disconnect previous client instance
    except Exception as e:
        print(f"Disconnect error: {e}")

    sleep(2)  # Small delay before reconnecting
    gc.collect()  # Manually run garbage collection
    client = connect_and_subscribe()  # Create a new connection

# Start Wi-Fi connection
wlan = connect_wifi()

try:
    client = connect_and_subscribe()
except OSError:
    client = None
    restart_reconnect()

# Initialize PiChart
pressure_chart = pichart.Chart(display, title="Pressure (hPa)")
pressure_chart.set_values(pressure)  # Initial values
pressure_chart.min_val = 900  # Typical min atmospheric pressure in hPa
pressure_chart.max_val = 1100  # Typical max atmospheric pressure in hPa
container = pichart.Container(display)
container.add_chart(pressure_chart)
container.update()
container.data_colour = {'red': 0, 'green': 0, 'blue': 255}  # Blue data
pressure_chart.show_datapoints = True
pressure_chart.show_lines = True
pressure_chart.show_bars = False
pressure_chart.grid = True

temperature_chart = pichart.Chart(display, title="Temperature (°C)")
temperature_chart.set_values(temperature)  # Initial values
temperature_chart.min_val = -10  # Typical min temperature in °C
temperature_chart.max_val = 30  # Typical max temperature in °C
temperature_chart.show_values = True

container.add_chart(temperature_chart)
container.update()

forecast_card = pichart.Card(display, title="Forecast")
forecast_card.title = "Forecast"
forecast_card.background_colour = {'red': 0, 'green': 0, 'blue': 255}
forecast_card.data_colour = {'red': 255, 'green': 255, 'blue': 255}
forecast_card.show_border = True
forecast_card.update()
container.add_chart(forecast_card)
container.cols = 2

# Main loop: Poll MQTT and update display
while True:
    try:
        client.check_msg()  # Process incoming MQTT messages
    except OSError as e:
        print(f"MQTT Error: {e}")
        restart_reconnect()

    # Update Display
#     display.set_pen(BLUE)
#     display.clear()
#     display.set_pen(WHITE)
#     display.text(prediction, 0, 0, WIDTH, 2)
    
    # Update chart with latest pressure values
    pressure_chart.set_values(pressure)  # Update chart data
    forecast_card.title = prediction  # Update forecast
    temperature_chart.set_values(temperature)
#     pressure_chart.update()
    container.update()
    presto.update()
    
    gc.collect()  # Free up memory every loop iteration
    sleep(5)  # 5s update interval