# #! /bin/MicroPython
import time

import network
from machine import Pin


def do_connect(ssid: str, password: str, status_led: Pin, timeout_seg: int = 30) -> bool:
    """
    Initializes a Wi-Fi station connection with visual feedback and timeout management.

    :param ssid: Service Set Identifier of the target network.
    :param password: Network security key.
    :param status_led: machine.Pin object for visual status indication.
    :param timeout_seg: Maximum time in seconds to attempt connection.
    :return: True if connection is successful, False otherwise.
    """
    wlan = network.WLAN(network.STA_IF)

    # Preventive stack reset to ensure clean initialization
    if wlan.active():
        wlan.active(False)
        time.sleep_ms(100)

    wlan.active(True)

    if not wlan.isconnected():
        print(f'Connecting to {ssid} (timeout: {timeout_seg}s)...')
        wlan.connect(ssid, password)

        start_time = time.ticks_ms()

        # Non-blocking polling loop with LED toggling
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start_time) > (timeout_seg * 1000):
                print('\nConnection timeout.')
                status_led.off()
                wlan.active(False)
                return False

            print('.', end='')
            status_led.toggle()
            time.sleep_ms(500)

    # Steady state LED indicates successful connection
    if wlan.isconnected():
        status_led.on()
        print('\nConnected!')
        print('IP Address:', wlan.ifconfig()[0])
        return True
