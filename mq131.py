from machine import Pin, SoftI2C
import time


class MQ131:
    def __init__(self):
        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
        self.memAdr = 80 #"0x50" en hex.
        self.RO_LIMPIO = 0
        self.RL_VALUE = None
        self.scan()
    
    def scan(self):
        x = self.i2c.scan()

        if len(x) == 0:
            return -1
        else: 
            print("found sth..")

            for device in x:
                print("Addr", device, "Hex", hex(device))
    

    def read(self):
        #conversion
        x = self.i2c.readfrom_mem(0x50, 0x00, 2)
        num = int.from_bytes(x, "big")
        ppm = (1.99 * num) / 4096 + 0.01
        print("received this", num)
        print("supposed ppm..", ppm)

sensor = MQ131()

while True:
    sensor.read()
    time.sleep(5)
