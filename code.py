import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_minimqtt import MQTT
from adafruit_pybadger import PyBadger
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

# try to use credentials from secrets.py file else raise an exception
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# configuration for esp32 airlift featherwing, works with PyBadge
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)
pybadger = PyBadger()
pybadger.pixels.fill(0)

# Setup a feed hierarchy for subscribing to changes
subscribe_feed = secrets['aio_username'] + '/feeds/#'

# Define callback methods which are called when events occur
def connected(client, userdata, flags, rc):
    # successfully to the broker.
    print('Connected to MQTT Broker! Listening for topic changes on %s' % subscribe_feed)
    client.subscribe(subscribe_feed)
    # basic badge render on successful connect of broker 
    pybadger.show_badge(name_string="<Your_Name>", hello_scale=2, my_name_is_scale=2, name_scale=3)

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print('Disconnected from MQTT BROKER!')

def message(client, topic, message):
    print('New message on topic {0}: {1}'.format(topic, message))

    # feed #1 on which we're listening to values of color is named RGB
    if topic == secrets['aio_username'] + '/feeds/RGB':
        RGB = [x.strip() for x in message.split('#')]
        val = int(RGB[1], 16)
        pybadger.pixels.fill(val)
        time.sleep(0.1)

    # feed #1 on which we're listening to values of name is named name
    elif topic == secrets['aio_username'] + '/feeds/name':
        pybadger.show_badge(name_string=message, hello_scale=2, my_name_is_scale=2, name_scale=3)

wifi.connect()

# Set up a MiniMQTT Client with broker address and api keys
mqtt_client = MQTT(socket,
                   broker='io.adafruit.com', 
                   username=secrets['aio_username'], 
                   password=secrets['aio_key'],
                   network_manager=wifi)

mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print('Connecting to MQTT BROKER...')
mqtt_client.connect()

while True:
    # Poll the message queue forever (BLOCKING!!)
    mqtt_client.loop_forever()