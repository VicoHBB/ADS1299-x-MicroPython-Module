# #! /bin/MicroPython
import time
import network

def main():
    """Main Function
    :returns: None
    """
    wlan = network.WLAN(network.STA_IF)

    if wlan.active():
        wlan.active(False)
        time.sleep_ms(100)

    wlan.active(True)  # Always active after reset

    print(f"Scan networks...")
    networks = [r[0].decode("utf-8") for r in wlan.scan()]
    print(f"Networks available: {networks}")
    pass

if __name__ == "__main__":
    main()
