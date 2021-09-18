from machine import UART
import time


class DGSULPSO2:
    def __init__(self):
        self.uart = UART(1, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1, tx=16, rx=17, timeout=1)
        self.line = ''
        self.ppm = 0
    
    def start(self):
        self.uart.write('c')
        print('Sent start command to SO2 Sensor')
        time.sleep(5)
    
    def stop(self):
        self.uart.write('r')
        print('Stopped recording SO2 Sensor')

    def get_reading(self):
        print('Reading...')
        self.line = self.uart.readline()
        time.sleep(3)
        print('got this line', self.line)

    #tenemos que calibrar luego de dejar conectado por 8-24h.
    def calibrate(self):
        # lo dejamos en continous mode.
        self.uart.write('c')
        print('Calibrating, please leave the sensor connected to the device for at least 1 hour')
        time.sleep(3600)
        print('Done calibrating.')
        self.uart.write('Z')
        time.sleep(10)
        self.uart.write('12345\r')

    def parse(self):
        if self.line:
            params = self.line.decode('utf-8').split(',')
            if len(params) < 10:
                pass
            else:
                self.ppm = int(params[1]) / 1000 #dado que viene en ppb
                print('Reporting ppm SO2 ', self.ppm)





sensor = DGSULPSO2()
sensor.start()

try:
    while True:
        sensor.get_reading()
        time.sleep(5)
        sensor.parse()
except KeyboardInterrupt:
    print('Stopping everything.')

finally: 
    sensor.stop()
    time.sleep(5)
    print('Graceful exit.')
