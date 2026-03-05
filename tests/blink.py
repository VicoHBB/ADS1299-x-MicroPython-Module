# #! /bin/MicroPython

import time
from machine import Pin, freq

led = Pin(2, Pin.OUT)

def main():
    while True:
        led.toggle()
        time.sleep_ms(500)

if __name__ == "__main__":
    main()
