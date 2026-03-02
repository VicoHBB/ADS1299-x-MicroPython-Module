# Import necessary modules
from machine import Pin, freq, SPI
from utime import sleep_ms
from module.ads1299 import ADS1299, make_config1, make_config3
import json

# Set the CPU frequency to 240Mhx
# This can help optimize the performance of the microcontroller
freq(240000000)

# Declare CS (Chip Select) Pin for the ADS1299
cs = Pin(5, Pin.OUT, value=1)
# Declare DRDY (Data Ready) Pin for synchronization
drdy = Pin(4, Pin.IN, Pin.PULL_UP)

data_ready = False

def irq_handler(pin: Pin) -> None:
    global data_ready
    data_ready = True
    pass


# Configure SPI communication with the ADS1299
# SPI settings are CPOL = 0 and CPHA = 1
spi = SPI(2, baudrate=16000000, polarity=0, phase=1, bits=8,
          firstbit=SPI.MSB, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# Initialize the ADS1299 with the configured SPI and CS pins
ads = ADS1299(cs, spi)

# Set the samples rate to 500sps
cf1 = make_config1(data_rate=ADS1299.SAMPLE_RATE_500)

# Set the internal reference buffer to power down mode
cf3 = make_config3(pwr_down_refbuf=True)

# Initialize the ADS1299 with the configuration settings
ads.init(config1=cf1,config3=cf3)

# Configure all channels to be active, with a gain of 2 and normal input
ads.config_all_channels(
    channels_active=8, gain=ADS1299.GAIN_2, channel_input=ADS1299.NORMAL)

# Example of how to configure individual channels using the write_register()
# method
# To test it, import make_schnset function from ads1299.py
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

# Configures before start
drdy.irq(trigger=Pin.IRQ_FALLING, handler=irq_handler)

# Read all the registers of the ADS1299 and print their values
regs = ads.read_all_registers()
for i in regs:
    print(hex(i))

# Create a dictionary to store the data from each channel
dictionary = {f'Ch{i}': [] for i in range(8)}
# Pre-extramos las referencias a las listas para máxima velocidad
channel_list = tuple(dictionary[f'Ch{i}'] for i in range(8))

print("Test read_continuous")
# Enable continuous reading from the ADS1299
ads.enable_read_continuous()

#Take 1000 samples
# for sample in range(500):
#
#     # Wait for DRDY pin to go LOW (indicates data is ready)
#     while drdy.value():
#         pass
#
#     # Read the channels continuously from the ADS1299
#     _, channels_data = ads.read_channels_continuous()
#
#     for i in range(8):
#         channel_list[i].append(channels_data[i])

samples = 0

#Take 500 samples
while samples < 500:

    if data_ready:
        data_ready = False
        # Read the channels continuously from the ADS1299
        _, channels_data = ads.read_channels_continuous()

        for i in range(8):
            channel_list[i].append(channels_data[i])

        samples += 1
    else:
        pass

# Disable interruption
drdy.irq(handler=None)
ads.disable_read_continuous()


# print("Test read_channels_once:")
# for i in range(500):
#     # Wait for DRDY pin to go LOW (indicates data is ready)
#     while drdy.value():
#         pass
#
#     # Read the channels once from the ADS1299
#     _, channels_data = ads.read_channels_once()
#
#     for j in range(8):
#         channel_list[j].append(channels_data[j])


print(dictionary) # View data

# Store data in a json file, this is just for plot it
with open("signals.json", "w") as jsonFile:
    json.dump(dictionary, jsonFile)

# Clear the dictionary to prepare for the next set of readings
for i in range(8):
    dictionary[f'Ch{i}'].clear()
