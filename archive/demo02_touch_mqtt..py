from presto import Presto
from touch import Button
from umqttsimple import MQTTClient
from WIFI_CONFIG import SSID, PASSWORD
import network
from time import sleep
import gc

MQTT_SERVER = "192.168.1.10"
MQTT_TOPIC = "cluster/status"
MQTT_CLIENT_ID = "touch_demo"
MQTT_PORT = 1883

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
    print(f"Connecting to MQTT: {MQTT_CLIENT_ID} @ {MQTT_SERVER}:{MQTT_PORT}")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, keepalive=30)
    client.connect()
    # client.subscribe(MQTT_TOPIC)
    return client

def restart_reconnect(client=None):
    """ Attempt to reconnect to MQTT on failure, cleaning up memory. """
    print('Reconnecting to MQTT...')
    if client is not None:
        try:
            client.disconnect()  # Disconnect previous client instance
        except Exception as e:
            print(f"Disconnect error: {e}")

    sleep(2)  # Small delay before reconnecting
    gc.collect()  # Manually run garbage collection
    return connect_and_subscribe()  # Create and return a new connection

# Start Wi-Fi connection
wlan = connect_wifi()

# Initial MQTT connection
try:
    print('connecting to mqtt')
    client = connect_and_subscribe()
except OSError:
    client = restart_reconnect()

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Couple of colours for use later
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(230, 60, 45)
GREEN = display.create_pen(9, 185, 120)
BLACK = display.create_pen(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

CX = WIDTH // 2
CY = HEIGHT // 2
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

# Create a touch button and set the touch region
button_1 = Button(10, 35, BUTTON_WIDTH, BUTTON_HEIGHT)
button_2 = Button(10, 95, BUTTON_WIDTH, BUTTON_HEIGHT)
button_3 = Button(10, 155, BUTTON_WIDTH, BUTTON_HEIGHT)

while True:
    # Check for touch changes
    touch.poll()

    # Clear the screen and set the background colour
    display.set_pen(WHITE)
    display.clear()
    display.set_pen(BLACK)

    # Title text
    display.text("Touch Button Demo", 23, 7)

    # Button 1
    if button_1.is_pressed():
        display.set_pen(GREEN)
        display.text("You Pressed\nButton 1!", (button_1.x + button_1.w) + 20, button_1.y + 3, 100, 2)
        try:
            client.publish(MQTT_TOPIC, "warning")
        except Exception as e:
            print(f"Publish failed: {e}")
            client = restart_reconnect(client)
    else:
        display.set_pen(RED)
    display.rectangle(*button_1.bounds)

    # Button 2
    if button_2.is_pressed():
        display.set_pen(GREEN)
        display.text("You Pressed\nButton 2!", (button_2.x + button_2.w) + 20, button_2.y + 3, 100, 2)
        try:
            client.publish(MQTT_TOPIC, "normal")
        except Exception as e:
            print(f"Publish failed: {e}")
            client = restart_reconnect(client)
    else:
        display.set_pen(RED)
    display.rectangle(*button_2.bounds)

    # Button 3
    if button_3.is_pressed():
        display.set_pen(GREEN)
        display.text("You Pressed\nButton 3!", (button_3.x + button_3.w) + 20, button_3.y + 3, 100, 2)
        try:
            client.publish(MQTT_TOPIC, "alert")
        except Exception as e:
            print(f"Publish failed: {e}")
            client = restart_reconnect(client)
    else:
        display.set_pen(RED)
    display.rectangle(*button_3.bounds)

    # Finally, we update the screen so we can see our changes!
    presto.update()