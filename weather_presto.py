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
MQTT_CLIENT_ID = "weather"

pressure = [1,1,1,1]

# Global variable for prediction text (fixed-size buffer to prevent fragmentation)
prediction = "Waiting for prediction..."[:50]

def sub_cb(topic, msg):
    """ MQTT Subscribe Callback: Updates global variable with received message. """
    global prediction, pressure
    msg = msg.decode("utf-8")
    if topic =="weather/prediction":
    
        print(f'Received MQTT: topic={topic.decode("utf-8")}, msg={msg}')
        
        # Use fixed-size slicing to avoid memory fragmentation
        prediction = msg[:50]  # Trim message to prevent memory issues
    elif topic =="weather/pressure":
        pressure = json.loads(msg)
        print(f"Pressure data is {pressure}")

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
    """ Connect to MQTT broker and subscribe to a topic. """
    global MQTT_CLIENT_ID, MQTT_SERVER

    print(f"Connecting to MQTT: {MQTT_CLIENT_ID} @ {MQTT_SERVER}:{MQTT_PORT} on {MQTT_TOPIC}")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, keepalive=30)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    client.subscribe(PRESSURE_TOPIC)
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

chart = pichart.Chart(display, title="Pressure")
print(f"Pressure values are: {pressure}")
chart.set_values = pressure
chart.min_val = 1
chart.max_val = 100
container = pichart.Container(display)
container.add_chart(chart)
container.update()

# Main loop: Poll MQTT and update display
while True:
    try:
        client.check_msg()  # Process incoming MQTT messages
    except OSError as e:
        print(f"MQTT Error: {e}")
        restart_reconnect()

    # Update Display
    display.set_pen(BLUE)
    display.clear()
    display.set_pen(WHITE)
    display.text(prediction, 0, 0, WIDTH, 2)
    chart.x_values = pressure 
    container.update()
    presto.update()
    
    gc.collect()  # Free up memory every loop iteration
    sleep(5)  # Reduce CPU usage with a 5s update interval
