# Import necessary modules
from machine import Pin, freq, SPI
from utime import sleep_ms
from module.ads1299 import ADS1299, make_config1, make_config3
import json

# Set the CPU frequency to 240Mhx (Maximum frequency)
# This can help optimize the performance of the microcontroller
# @NOTE: Looks like Micro firmware does not work properly with maximum frequency
freq(240000000)

# Declare CS (Chip Select) Pin for the ADS1299
cs = Pin(2, Pin.OUT)

# Configure SPI communication with the ADS1299
# SPI settings are CPOL = 0 and CPHA = 1
spi = SPI(1, 4000000, polarity=0, phase=1, bits=8,
          firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(13), miso=Pin(12))

# Initialize the ADS1299 with the configured SPI and CS pins
ads = ADS1299(cs, spi)

# Set the sample rate to 500sps
cf1 = make_config1(data_rate=ADS1299.SAMPLE_RATE_500)

# Set the internal reference buffer to power down mode
cf3 = make_config3(pwr_down_refbuf=True)

# Initialize the ADS1299 with the configuration settings
ads.init(config1=cf1, config3=cf3)

# Configure all channels to be active, with a gain of 2 and normal input
# in a single instruction with method config_all_channels()
ads.config_all_channels(
    channels_active=8, gain=ADS1299.GAIN_2, channel_input=ADS1299.NORMAL)

# Create a dictionary to store the data from each channel
dictionary = {f'Ch{i}': [] for i in range(8)}

# Enable continuous reading from the ADS1299
ads.enable_read_continuous()

# Infinite loop to continuously read and store data
while True:
    for i in range(250):
        # Read the channels continuously from the ADS1299
        channels = ads.read_channels_continuous()
        # Store the reading from each channel in the dictionary
        for i in range(8):
            dictionary[f'Ch{i}'].append(channels[i])
        # Wait for 1 ms before taking the next reading
        sleep_ms(1)

    # Convert the dictionary to a JSON string
    jsonString = json.dumps(dictionary)

    # Open a file named "signals.json" in write mode
    jsonFile = open("signals.json", "w")
    # Write the JSON string to the file
    jsonFile.write(jsonString)
    # Close the file
    jsonFile.close()

    # Clear the dictionary to prepare for the next set of readings
    for i in range(8):
        dictionary[f'Ch{i}'].clear()
