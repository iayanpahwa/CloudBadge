import time
import board
import busio
import neopixel
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

# Lanyard Neopixel Setup
pixel_pin = board.D2
num_pixels = 50
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)
pixels.fill((0, 0, 0))
pixels.show()

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)
pybadger = PyBadger()
#pybadger.show_badge(name_string="AYAN", hello_scale=2, my_name_is_scale=2, name_scale=3)
pybadger.pixels.fill(0)

# Setup a feed hierarchy for subscribing to changes
subscribe_feed = secrets['aio_username'] + '/feeds/#'

# Define callback methods which are called when events occur
def connected(client, userdata, flags, rc):
    # successfully to the broker.
    print('Connected to MQTT Broker! Listening for topic changes on %s' % subscribe_feed)
    client.subscribe(subscribe_feed)
    # basic badge render
    pybadger.show_badge(name_string="Ayan", hello_scale=2, my_name_is_scale=2, name_scale=3)

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print('Disconnected from MQTT BROKER!')


def message(client, topic, message):
    print('New message on topic {0}: {1}'.format(topic, message))

    # feed #1 on which we're listening to values of color is named RGB
    if topic == "iayanpahwa/feeds/RGB":
        RGB = [x.strip() for x in message.split('#')]
        val = int(RGB[1], 16)
        pybadger.pixels.fill(val)
        pixels.fill(val)
        pixels.show()
        time.sleep(0.1)

    # feed #1 on which we're listening to values of name is named name
    elif topic == "iayanpahwa/feeds/name":
        pybadger.show_badge(name_string=message, hello_scale=2, my_name_is_scale=2, name_scale=3)


wifi.connect()

# Set up a MiniMQTT Client
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

    #pybadger.auto_dim_display(delay=10) # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        pybadger.show_business_card(image_name="Blinka.bmp", name_string="Ayan Pahwa", name_scale=2,
                                    email_string_one="iayanpahwa", email_string_two="@gmail.com")
    elif pybadger.button.b:
        pybadger.show_qr_code(data="https://codeNsolder.com")
    elif pybadger.button.start:
        pybadger.show_badge(name_string="AYAN", hello_scale=2, my_name_is_scale=2, name_scale=3)