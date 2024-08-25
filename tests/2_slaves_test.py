from machine import Pin, freq, SPI
from utime import sleep_ms
from ads1299 import ADS1299
from ads1299 import make_config3, make_chnset
import json

# Set the CPU frequency to 240MHz
freq(240000000)

# Define CS pins for both ADS1299 devices
cs1 = Pin(2, Pin.OUT)
cs2 = Pin(4, Pin.OUT)

# SPI settings: CPOL = 0, CPHA = 1, 4MHz clock, 8-bit mode, MSB first
spi = SPI(1, 4000000, polarity=0, phase=1, bits=8,
          firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(13), miso=Pin(12))

# Create instances of the ADS1299 class for both devices
ads1 = ADS1299(cs1, spi)
ads2 = ADS1299(cs2, spi)

# Set internal reference for both devices
cf3 = make_config3(pwr_down_refbuf=True)

# Initialize both ADS1299 devices with the internal reference configuration
ads1.init(config3=cf3)
ads2.init(config3=cf3)

# Configure all channels of ADS1299 device 1 with the method config_all_channels()
ads1.config_all_channels(
    channels_active=4, gain=ADS1299.GAIN_2, channel_input=ADS1299.NORMAL)

# Configure channels of ADS1299 device 2 with the method write_registers()
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

# Read all registers of both ADS1299 devices
ads1_regs = ads1.read_all_registers()
ads2_regs = ads2.read_all_registers()

# Print the configuration registers of both ADS1299 devices
print("ads1_regs:", "ads2_regs")
for i in range(len(ads1_regs)):
    print(hex(ads1_regs[i]), hex(ads2_regs[i]))

# Create a dictionary to store the data from both ADS1299 devices
dictionary = {f'Ch{i}': [] for i in range((16))}

# Enable continuous reading for both ADS1299 devices
ads1.enable_read_continuous()
ads2.enable_read_continuous()

# Run the data collection for 200 samples
for i in range(200):
    # Read data from both ADS1299 devices
    channels_0_7 = ads1.read_channels_continuous()
    channels_8_15 = ads2.read_channels_continuous()

    # Store the data in the dictionary
    for j in range(8):
        dictionary[f'Ch{j}'].append(channels_0_7[j])

    for j in range(8, 16):
        dictionary[f'Ch{j}'].append(channels_8_15[j-8])

    # Wait 1 ms before taking the next sample
    sleep_ms(1)

# Convert the dictionary to a JSON string
jsonString = json.dumps(dictionary)

# Write the JSON string to a file for further analysis or transmission
jsonFile = open("signals.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

# Clear the dictionary to free up memory
for i in range(16):
    dictionary[f'Ch{i}'].clear()

# Disable continuous reading for both ADS1299 devices
ads1.disable_read_continuous()
ads2.disable_read_continuous()
