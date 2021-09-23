from machine import UART
import time


class DGSULPSO2:
    def __init__(self):
        self.uart = UART(1, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1, tx=17, rx=16, timeout=1)
        self.line = ''
        self.ppm = 0
        self.heating = False
    
    def start(self):
        self.uart.write('c')
        print('Sent start command to SO2 Sensor')
        time.sleep(5)
    
    def stop(self):
        self.uart.write('r')
        print('Stopped recording SO2 Sensor')

    def get_reading(self):
        self.line = self.uart.readline()
        print(self.line)
        time.sleep(3)

    #tenemos que calibrar luego de dejar conectado por 8-24h.
    def calibrate(self, stop=3600):
        # lo dejamos en continous mode.
        self.uart.write('c')
        print('Waiting for ADC stabilization for', stop, "seconds")

        #toWrite = "082720010324 110601 SO2 1509 39.47"
       
        

            

    def parse(self):
        if self.line:
            params = self.line.decode('utf-8').split(',')
            if len(params) < 10:
                pass
            else:
                if not self.heating:
                    ppm = int(params[1]) / 1000 #dado que viene en ppb
                    if ppm < 0:
                        # lo dejamos quince minutos en standby.
                        print('Starting zero calibrate.')
                        self.calibrate(900)
                        self.ppm = -1
                    else:
                        self.ppm = ppm
                        print('Reporting ppm SO2 ', self.ppm)
                else:
                    self.ppm = -1




"""
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
"""