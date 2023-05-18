from machine import Pin, freq, SPI
from utime import sleep_ms
from ads1299 import ADS1299
from ads1299 import make_config3, make_chnset
import json

# Set the CPU frequency to 240Mhx
freq(240000000)

# Declar CS Pin
cs1 = Pin(2, Pin.OUT)
cs2 = Pin(4, Pin.OUT)
# SPI settings are CPOL = 0 and CPHA = 1
spi = SPI(1, 4000000, polarity=0, phase=1, bits=8,
          firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(13), miso=Pin(12))

ads1 = ADS1299(cs1, spi)
ads2 = ADS1299(cs2, spi)

# Set internal reference
cf3 = make_config3(pwr_down_refbuf=True)

ads1.init(config3=cf3)  # ADS1299 startup routine
ads2.init(config3=cf3)  # ADS1299 startup routine

# Config all channels with the method config_all_channels()
ads1.config_all_channels(
    channels_active=4, gain=ADS1299.GAIN_2, channel_input=ADS1299.NORMAL)


# Config channels with method write_register()

ads2.write_registers(ADS1299.CH1SET, [
    make_chnset(power_down=True),  # Power down channel
    make_chnset(gain=ADS1299.GAIN_4, channel_input=ADS1299.NORMAL),
    make_chnset(power_down=True),  # Power down channel
    make_chnset(gain=ADS1299.GAIN_4, channel_input=ADS1299.NORMAL),
    make_chnset(power_down=True),  # Power down channel
    make_chnset(gain=ADS1299.GAIN_4, channel_input=ADS1299.NORMAL),
    make_chnset(power_down=True),  # Power down channel
    make_chnset(gain=ADS1299.GAIN_4, channel_input=ADS1299.NORMAL)
])

ads1_regs = ads1.read_all_registers()
ads2_regs = ads2.read_all_registers()

print("ads1_regs:", "ads2_regs")
for i in range(len(ads1_regs)):
    print(hex(ads1_regs[i]), hex(ads2_regs[i]))

# create a dictionary to store the data
dictionary = {f'Ch{i}': [] for i in range((16))}

ads1.enable_read_continuous()       # Enable continuous reading for ads1
ads2.enable_read_continuous()       # Enable continuous reading for ads2

"""
RUN ONE TIME
"""
for i in range(250):
    # Take a reading from the ADS1299's
    channels_0_7 = ads1.read_channels_continuous()
    channels_8_15 = ads2.read_channels_continuous()

    # Store the reading in the dictionary
    for j in range(8):
        dictionary[f'Ch{j}'].append(channels_0_7[j])

    for j in range(8, 16):
        dictionary[f'Ch{j}'].append(channels_8_15[j-8])

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
for i in range(16):
    dictionary[f'Ch{i}'].clear()

ads1.disable_read_continuous()       # Disable continuous reading for ads1
ads2.disable_read_continuous()       # Disable continuous reading for ads2
