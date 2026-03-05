# #! /bin/MicroPython
import json
from ring_buffer import RingBuffer

from machine import SPI, Pin, freq
from utime import sleep_ms

from module.ads1299 import ADS1299, make_chnset, make_config1, make_config3

########################################################################################################################
#                                                       GLOBALS                                                        #
########################################################################################################################

data_ready = False # Declare data_ready at the top to use in every function

# Set the CPU frequency to 240Mhx
# This can help optimize the performance of the microcontroller
freq(240000000)

cs = Pin(5, Pin.OUT, value=True)   # Declare CS (Chip Select) Pin for the ADS1299
drdy = Pin(4, Pin.IN, Pin.PULL_UP) # Declare DRDY (Data Ready) Pin for synchronization

# Configure SPI communication with the ADS1299
# SPI settings are CPOL = 0 and CPHA = 1
spi = SPI(2, baudrate=16000000, polarity=0, phase=1, bits=8, firstbit=SPI.MSB, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

########################################################################################################################
#                                                      FUNCTIONS                                                       #
########################################################################################################################

def irq_handler(pin: Pin) -> None:
    """
    Interrupt Callback

    :param pin: The machine.Pin instance that triggered the interrupt.
    :return: None
    """
    global data_ready
    data_ready = True
    pass

def main() -> None:
    """Main Function
    :returns: None
    """
    ###################################################################################################################
    #                                                     INIT                                                        #
    ###################################################################################################################
    global data_ready # Indicates that is global
    data_ready = False

    ads = ADS1299(cs, spi)                               # Initialize the ADS1299 with the configured SPI and CS pins
    cf1 = make_config1(data_rate=ADS1299.SAMPLE_RATE_1K) # Set the samples rate to 500sps
    cf3 = make_config3(pwr_down_refbuf=True)             # Set the internal reference buffer to power down mode

    ads.init(config1=cf1,config3=cf3) # Initialize the ADS1299 with the configuration settings

    # Configure all channels to be active, with a gain of 2 and normal input
    ads.config_all_channels(channels_active=8, gain=ADS1299.GAIN_1, channel_input=ADS1299.NORMAL)

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

    # Read all the registers of the ADS1299 and print their values
    print("--- ADS1299 Internal Test Signals Config ---")
    regs = ads.read_all_registers()
    for addr, val in enumerate(regs):
        print("Reg 0x{:02x}: 0x{:02x}".format(addr, val))

    # Create a dictionary for the final output
    dictionary = {f'Ch{i}': [] for i in range(8)}

    # Pre-allocate Circular Buffers for each channel (1000 samples each)
    # This avoids .append() and heap allocation during acquisition
    channel_queues = tuple(RingBuffer(1000) for _ in range(8))

    ###################################################################################################################
    #                                                      APP                                                        #
    ###################################################################################################################
    print("Test read_continuous (With Ring Buffer)")
    # Enable continuous reading from the ADS1299
    ads.enable_read_continuous()

    # Enable irq
    drdy.irq(trigger=Pin.IRQ_FALLING, handler=irq_handler)

    # Read until the circular buffers are full (zero allocation)
    while not channel_queues[0].is_full():
        if data_ready:
            data_ready = False
            # Read the channels continuously from the ADS1299
            _, channels_data = ads.read_channels_continuous()

            # Write to queue instead of appending to list
            for i in range(8):
                channel_queues[i].write(channels_data[i])
        else:
            pass

    # Disable interruption
    ads.disable_read_continuous()
    drdy.irq(handler=None)

    # Once sampling is complete, extract data to dictionary for JSON serialization
    for i in range(8):
        q = channel_queues[i]
        target_list = dictionary[f'Ch{i}']
        while not q.is_empty():
            target_list.append(q.read())

    print(dictionary) # View data ()

    # Store data in a json file, this is just for plot it
    with open("signals.json", "w") as jsonFile:
        json.dump(dictionary, jsonFile)

    # Clear the dictionary to prepare for the next set of readings
    for i in range(8):
        dictionary[f'Ch{i}'].clear()


if __name__ == "__main__":
    main()
