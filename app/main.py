from machine import Pin, freq, SPI
from utime import sleep_ms
from ads1299 import ADS1299
import json

# Set the CPU frequency to 240Mhx
freq(240000000)
# Declar CS Pin
cs = Pin(2, Pin.OUT)
# SPI settings are CPOL = 0 and CPHA = 1
spi = SPI(1, 4000000, polarity=0, phase=1, bits=8,
          firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
ads = ADS1299(cs, spi)

cs.on()                            # Enable the communication

ads.init()                         # ADS1299 startup routine
ads.config_channels(7, 1, 0, 0x0)  # Set the configuration of channels 7 and 1

# Read the channel register to check for correct writing
for i in range(8):
    ads.read_register(ADS1299.CH1SET + i, 1)

# create a dictionary to store the data
dictionary = {f'Ch{i}': [] for i in range((8))}

ads.enable_read_continuous()       # Enable continuous reading

while True:

    for i in range(256):
        # Take a reading from the ADS1299
        channels = ads.read_channels_continuous()
        # Store the reading in the dictionary
        for i in range(8):
            dictionary[f'Ch{i}'].append(channels[i])
        # Wait 4 ms
        sleep_ms(4)

    # This sectiion creates a JSON string to post via WIFI
    # but ins this code just creates string
    jsonString = json.dumps(dictionary)

    # Clear the dictionary
    for i in range(8):
        dictionary[f'Ch{i}'].clear()
