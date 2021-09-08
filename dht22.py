import dht
from machine import Pin
import time

sensor = dht.DHT22(Pin(23))
while True:
    print("Measuring.")
    
    retry = 0
    while retry < 3:
        try:
            sensor.measure()
            break
        except:
            retry = retry + 1
            print(".", end = "")

    print("")

    if retry < 3:
        print("Temperature: %3.1f °C" % sensor.temperature())
        print("   Humidity: %3.1f %% RH" % sensor.humidity())

    time.sleep(5)