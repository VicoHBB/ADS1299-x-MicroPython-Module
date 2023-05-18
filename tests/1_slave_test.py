from machine import Pin, freq, SPI
from utime import sleep_ms
from ads1299 import ADS1299
from ads1299 import make_config3
# from ads1299 import make_chnset
import json

# Set the CPU frequency to 240Mhx
freq(240000000)
# Declar CS Pin
cs = Pin(2, Pin.OUT)
# SPI settings are CPOL = 0 and CPHA = 1
spi = SPI(1, 4000000, polarity=0, phase=1, bits=8,
          firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
ads = ADS1299(cs, spi)


# Set internal reference
cf3 = make_config3(pwr_down_refbuf=True)

ads.init(config3=cf3)  # ADS1299 startup routine

ads.config_all_channels(
    channels_active=8, gain=ADS1299.GAIN_2, channel_input=ADS1299.NORMAL)

# Config channels with method write_register()
# ads.write_registers(ADS1299.CH1SET, [
#     make_chnset(power_down=True, gain=ADS1299.NO_GAIN),  # Power down channel
#     make_chnset(gain=ADS1299.GAIN_4, channel_input=ADS1299.NORMAL),
#     make_chnset(power_down=True, gain=ADS1299.NO_GAIN),  # Power down channel
#     make_chnset(gain=ADS1299.GAIN_6, channel_input=ADS1299.NORMAL),
#     make_chnset(power_down=True, gain=ADS1299.NO_GAIN),  # Power down channel
#     make_chnset(gain=ADS1299.GAIN_8, channel_input=ADS1299.NORMAL),
#     make_chnset(power_down=True, gain=ADS1299.NO_GAIN),  # Power down channel
#     make_chnset(gain=ADS1299.GAIN_12, channel_input=ADS1299.NORMAL)
# ])

regs = ads.read_all_registers()

for i in regs:
    print(hex(i))

# create a dictionary to store the data
dictionary = {f'Ch{i}': [] for i in range((8))}

ads.enable_read_continuous()       # Enable continuous reading

"""
RUN ONE TIME
"""
for i in range(250):
    # Take a reading from the ADS1299
    channels_config = ads.read_channels_continuous()
    # Store the reading in the dictionary
    for i in range(8):
        dictionary[f'Ch{i}'].append(channels_config[i])
    # Wait 4 ms
    sleep_ms(1)

# This sectiion creates a JSON string to post via WIFI
# but ins this code just creates string
jsonString = json.dumps(dictionary)
# To see the signals we're gonna create a file a print the content of this
jsonFile = open("signals.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

# Clear the dictionary
for i in range(8):
    dictionary[f'Ch{i}'].clear()
