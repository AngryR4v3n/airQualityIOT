from machine import Pin, ADC
import math
import time
import dht
RO_LIMPIO = 6.22
class MQ5:
    def __init__(self):
        # este es un ratio...
        #self.R0_LIMPIO = 6.22 #valores iniciales en datasheet.
        self.RO_LIMPIO = 3300
        self.RL_VALUE = 1000 #Resistencia en el MQ5 en ohms
        self.rs = 0
        self.r0 = 0
        self.ppm = 0
        #33 humidity
        self.pointsH1 = [1.3745, 1.1718, 1.0881, 1.0441, 0.9934, 0.9449, 0.8921, 0.8480]
        #85 humidity
        self.pointsH2 = [1.1300,  0.9956, 0.9449, 0.8943, 0.8348, 0.7863, 0.7489, 0.7093]
        #para ambas graficas
        self.x_points = [-10, 0, 10, 20, 30, 40, 50]

        #curva de grafica log-log
        self.paramA = 933110825
        self.paramB = -14.10743
    
    def get_resistance(self):
        valor = ADC(Pin(32)).read()
        res = ((self.RL_VALUE * (4095 - valor)) / valor)
        self.rs = res

    def get_r0(self):
        self.r0 = self.rs * pow((self.paramA / 1), 1/self.paramB)
        return self.r0


    def get_temp_hum_gain(self,temp, hum):
        i = 0
        while temp > self.x_points[i] and i < len(self.x_points):
            i += 1

        #para temps extremas
        if i == len(self.x_points):

            rsRatio1 = self.pointsH1[i-1]
            rsRatio2 = self.pointH2[i-1]
        
        #para temps extremas..
        elif i == 0: 
            rsRatio1 = self.pointsH1[i]
            rsRatio2 = self.pointsH2[i]

        
        else:
            #interpolacion si esta dentro del intervalo [-10, 50]
            rsRatio1 = (self.pointsH1[i] - self.pointsH1[i-1]) / (self.x_points[i] - self.x_points[i-1]) * (temp - self.x_points[i]) + self.pointsH1[i]
            rsRatio2 = (self.pointsH2[i] - self.pointsH2[i-1]) / (self.x_points[i] - self.x_points[i-1]) * (temp - self.x_points[i]) + self.pointsH2[i]
            
            val = rsRatio1 + (hum - 33) * (rsRatio2 - rsRatio1) / (85-33)
        return val

    def get_corrected_r0(self, temp, hum):
        r0 = self.get_r0()
        m = self.get_temp_hum_gain(temp, hum)
        n = self.get_temp_hum_gain(20, 65)
        corrected = (n/m)*r0
        print('corrected R0', corrected)
        self.r0 = corrected


    def get_corrected_ppm(self, temp, hum):
        t = self.get_temp_hum_gain(temp, hum)

        #referencia segun documentacion.
        q = self.get_temp_hum_gain(20,65)
        res = self.rs * (q/t)
        print('corrected res', res)
        self.ppm = self.get_ppm(res)
    


    def get_ppm(self, rs_ro):
            return self.paramA * pow((rs_ro/self.r0), self.paramB);


class DHTSensor:
    def __init__(self):
        self.temp = 0
        self.hum = 0
        self.error = None
        self.dht_sensor = dht.DHT22(Pin(23))
    def get_temp_hum(self):
        retry = 0
        while retry < 3:
            try:
                self.dht_sensor.measure()
                break
            except:
                retry = retry + 1
                print(".", end = "")

            print("")

        if retry < 3:
            temp = self.dht_sensor.temperature()
            hum = self.dht_sensor.humidity()
            self.temp = temp
            self.hum = hum
            return temp, hum
        else:
            print("ERR: DHT22 Sensor unavailable.")
            self.error = 'DHT22 Sensor unavailable.'
            return -1,

"""
mq5 = MQ5()
tempSensor = DHTSensor()
#set R0
mq5.get_resistance()
tempSensor.get_temp_hum()
print("Initial temp", tempSensor.temp, tempSensor.hum)
mq5.get_corrected_r0(tempSensor.temp, tempSensor.hum)
print("SET R0", mq5.r0)
while True:
    if tempSensor.get_temp_hum() != -1:
        mq5.get_resistance()
        mq5.get_corrected_ppm(tempSensor.temp, tempSensor.hum)
        print("Corrected PPM: ", mq5.ppm)
    else:
        mq5.get_resistance()
        mq5.get_ppm()
        print("PPM: ", mq5.ppm)

    time.sleep(5)
"""