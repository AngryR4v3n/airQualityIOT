from machine import Pin, ADC
import math
import time
import dht
RO_LIMPIO = 6.22
class MQ5:
    def __init__(self):
        # este es un ratio...
        #self.R0_LIMPIO = 6.22 #valores iniciales en datasheet.
        self.RL_VALUE = 1000 #Resistencia en el MQ135 en ohms
        self.rs = 0
        self.r0 = 2300
        self.ppm = 0
        #33 humidity
        self.pointsH1 = [1.7164,1.2567,0.9996,0.9128]
        #85 humidity
        self.pointsH2 = [1.5396,  1.1410, 0.9096, 0.8228]
        #para ambas graficas
        self.x_points = [-9.86, 4.99, 19.99, 50]

        #curva de grafica log-log
        self.paramA = 764.4864
        self.paramB = -4.525248
    
    def get_resistance(self):
        valor = ADC(Pin(32)).read()
        res = ((self.RL_VALUE * (4095 - valor)) / valor)
        self.rs = res

    def get_r0(self):
        self.r0 = self.rs * pow((self.paramA / 0.01), 1/self.paramB)
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
       # r0 = self.get_r0()
        m = self.get_temp_hum_gain(temp, hum)
        n = self.get_temp_hum_gain(20, 65)
        corrected = (n/m)*self.r0
        self.r0 = corrected


    def get_corrected_ppm(self, temp, hum):
        t = self.get_temp_hum_gain(temp, hum)

        #referencia segun documentacion.
        q = self.get_temp_hum_gain(20,65)
        res = self.rs * (q/t)
        self.ppm = self.get_ppm(res)
    


    def get_ppm(self, rs_ro):
            return self.paramA * pow((rs_ro/self.r0), self.paramB);
