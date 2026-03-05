# #! /bin/MicroPython
import gc
import json
import socket
import network
from machine import Pin, SPI, freq
from utime import sleep_ms, ticks_us
from ring_buffer import RingBuffer
from wlan import do_connect
from module.ads1299 import ADS1299, make_config1, make_config3

########################################################################################################################
#                                                       GLOBALS                                                        #
########################################################################################################################

# Networking
SSID = "Put you wifi name here" # Check available networks with make look
PASSWORD = "Put you password here"
SERVER_IP = "Put you IP here"
SERVER_PORT = "Verify port here"


# Boost CPU for maximum throughput
freq(240000000)

# Hardware Pin Mapping
CS_PIN = const(5)
DRDY_PIN = const(4)
LED_PIN = const(2)

# Pre-formatted JSON string for maximum speed (bypass json.dumps)
_JSON_FMT = '{{"Ch0":{},"Ch1":{},"Ch2":{},"Ch3":{},"Ch4":{},"Ch5":{},"Ch6":{},"Ch7":{}}}\n'

# Global flags and objects
data_ready = False
cs = Pin(CS_PIN, Pin.OUT, value=True)
drdy = Pin(DRDY_PIN, Pin.IN, Pin.PULL_UP)
board_led = Pin(LED_PIN, Pin.OUT)

# SPI Configuration: 16MHz clock
spi = SPI(2, baudrate=16000000, polarity=0, phase=1, bits=8, firstbit=SPI.MSB,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

channel_queues = tuple(RingBuffer(256) for _ in range(8))
data_payload = {f'Ch{i}': 0 for i in range(8)}

########################################################################################################################
#                                                      FUNCTIONS                                                       #
########################################################################################################################

def irq_handler(pin: Pin) -> None:
    """
    Minimal ISR for DRDY pin.
    """
    global data_ready
    data_ready = True

def read_data(ads: ADS1299) -> None:
    """
    Reads continuous data from ADS1299 and pushes raw integers to queues.
    """
    _, channels_data = ads.read_channels_continuous()
    for i in range(8):
        channel_queues[i].write(channels_data[i])

def send_data(sock: socket.socket) -> None:
    """
    Extracts raw samples and sends them via TCP instantly using pre-formatted string.
    """
    while not channel_queues[0].is_empty():
        try:
            msg = _JSON_FMT.format(
                channel_queues[0].read(), channel_queues[1].read(),
                channel_queues[2].read(), channel_queues[3].read(),
                channel_queues[4].read(), channel_queues[5].read(),
                channel_queues[6].read(), channel_queues[7].read()
            )
            sock.send(msg.encode('utf-8'))

        except OSError as e:
            # Handle EAGAIN (WiFi buffer full) without blocking
            if e.args[0] == 11:
                break
            pass
        except Exception:
            pass

########################################################################################################################
#                                                        MAIN                                                          #
########################################################################################################################

def main() -> None:
    global data_ready

    if not do_connect(SSID, PASSWORD, board_led):
        return

    # ADS1299 HW Initialization
    ads = ADS1299(cs, spi)
    cf1 = make_config1(data_rate=ADS1299.SAMPLE_RATE_250)
    cf3 = make_config3(pwr_down_refbuf=True)

    ads.init(config1=cf1, config3=cf3)
    ads.config_all_channels(channels_active=8, gain=ADS1299.GAIN_1, channel_input=ADS1299.NORMAL)

    # TCP Socket setup
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((SERVER_IP, SERVER_PORT))
        # Disable Nagle's algorithm for zero TCP latency
        client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client_sock.setblocking(False)
    except Exception:
        print("Telemetry server unreachable.")

    # Acquisition Pipeline
    ads.enable_read_continuous()
    drdy.irq(trigger=Pin.IRQ_FALLING, handler=irq_handler)

    gc.collect()
    last_gc = ticks_us()
    ###################################################################################################################
    #                                                       APP                                                       #
    ###################################################################################################################
    try:
        while True:
            # PRIORITY 1: Fetch hardware data
            if data_ready:
                data_ready = False
                read_data(ads)

            # PRIORITY 2: Dispatch telemetry
            send_data(client_sock)

            # Maintenance: Periodic GC every 2s
            now = ticks_us()
            if ticks_us() - last_gc > 2000000:
                gc.collect()
                last_gc = now

    except KeyboardInterrupt:
        print("Stopping high-speed telemetry...")
    finally:
        ads.disable_read_continuous()
        drdy.irq(handler=None)
        client_sock.close()

if __name__ == "__main__":
    main()
