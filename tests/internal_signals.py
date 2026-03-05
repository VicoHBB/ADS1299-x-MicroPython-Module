# #! /bin/MicroPython
import json
from ring_buffer import RingBuffer
from machine import SPI, Pin, freq
from utime import sleep_ms
from module.ads1299 import ADS1299, make_config1, make_config2, make_config3

########################################################################################################################
#                                                       GLOBALS                                                        #
########################################################################################################################

data_ready = False

# Optimize ESP32 performance at 240MHz
freq(240000000)

# Hardware Configuration (Consistent with tests/1_slave_test.py)
cs = Pin(5, Pin.OUT, value=True)
drdy = Pin(4, Pin.IN, Pin.PULL_UP)

# SPI: 16MHz, CPOL=0, CPHA=1 (ADS1299 Standard)
spi = SPI(2, baudrate=16000000, polarity=0, phase=1, bits=8, firstbit=SPI.MSB,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

########################################################################################################################
#                                                      FUNCTIONS                                                       #
########################################################################################################################

def irq_handler(pin: Pin) -> None:
    """Interrupt callback for DRDY (Data Ready)"""
    global data_ready
    data_ready = True

def main() -> None:
    """Main flow for internal signal configuration and testing"""
    global data_ready
    data_ready = False

    ads = ADS1299(cs, spi)

    # 1. Global Register Configuration
    # CONFIG1: 500 SPS
    cf1 = make_config1(data_rate=ADS1299.SAMPLE_RATE_500)

    # CONFIG2: Enable internal test signal generation
    # test_source=True  -> INT_CAL = 1
    # signal_amp=1     -> 1x Amplitude (-(VREFP-VREFN)/2400)
    # signal_freq=PULSED_1 -> Frequency fCLK / 2^21 (~1Hz)
    cf2 = make_config2(test_source=True, signal_amp=1, signal_freq=ADS1299.PULSED_1)

    # CONFIG3: Enable internal reference (required for test signals)
    # biasref_signal=True -> (AVDD+AVSS)/2 generated internally
    cf3 = make_config3(pwr_down_refbuf=True, biasref_signal=True)

    # Initialize with test signal configuration
    ads.init(config1=cf1, config2=cf2, config3=cf3)

    # 2. Channel Configuration
    # MUXn[2:0] = 101 (ADS1299.TEST) to connect the MUX to the internal test signal on all 8 channels
    ads.config_all_channels(channels_active=8, gain=ADS1299.GAIN_1, channel_input=ADS1299.TEST)

    # Console register verification for debugging
    print("--- ADS1299 Internal Test Signals Config ---")
    regs = ads.read_all_registers()
    for addr, val in enumerate(regs):
        print("Reg 0x{:02x}: 0x{:02x}".format(addr, val))

    # Pre-allocate Ring Buffers for 1000 samples per channel (Prevents heap fragmentation)
    dictionary = {f'Ch{i}': [] for i in range(8)}
    channel_queues = tuple(RingBuffer(1000) for _ in range(8))

    # 3. Data Acquisition
    print("\nStarting continuous read. Capturing 1000 samples...")
    ads.enable_read_continuous()
    drdy.irq(trigger=Pin.IRQ_FALLING, handler=irq_handler)

    while not channel_queues[0].is_full():
        if data_ready:
            data_ready = False
            _, channels_data = ads.read_channels_continuous()

            # Write to circular buffers (Zero-allocation)
            for i in range(8):
                channel_queues[i].write(channels_data[i])

    # Interrupt and ADS1299 cleanup
    ads.disable_read_continuous()
    drdy.irq(handler=None)

    # Transfer buffers to dictionary for JSON serialization
    for i in range(8):
        q = channel_queues[i]
        target_list = dictionary[f'Ch{i}']
        while not q.is_empty():
            target_list.append(q.read())

    # Result storage
    print("Saving data to signals.json...")
    with open("signals.json", "w") as jsonFile:
        json.dump(dictionary, jsonFile)

    print("Test finished successfully.")

if __name__ == "__main__":
    main()
