from machine import Pin, ADC
import math
import time
import dht
RO_LIMPIO = 6.22
RL_VALUE = 1  # 1Kohm

class MQ5:
    def __init__(self):
        self.R0_LIMPIO = 6.22 #valores iniciales en datasheet.
        self.RL_VALUE = 1 #Resistencia en el MQ5
        self.rs = 0
        self.r0 = 0
        self.ppm = 0
        
    def get_resistance(self):
        valor = ADC(Pin(32)).read()
        res = ((RL_VALUE * (4095 - valor)) / valor)
        self.rs = res

    def get_rsro_tempHum(self,temp, hum):
        #val eq1 -> 30% hum
        #val eq2 -> 60% hum
        eq1 = -0.14214*(temp) + 1.8657
        eq2 = -0.1218*(temp) + 1.5843
        #se ejecuta interpolacion lineal entre las curvas.
        val = eq1 + (hum - 30) * (eq2 - eq1) / (60 - 30)

        return val

    def get_corrected_ppm(self, temp, hum):
        t = self.get_rsro_tempHum(temp, hum)
        #referencia segun documentacion.
        q = self.get_rsro_tempHum(20,65)
        print("t", t)
        print("q", q)
        res = self.rs * (q/t) /  1000
        self.ppm = self.get_ppm(res/self.r0)
    
    def calibration(self):
        Rs = 0
        for i in range(0,100):
            self.get_resistance()
            Rs += self.rs
            time.sleep(0.1)
   
        Rs = Rs / 100
        r0 = Rs/RO_LIMPIO
        self.r0 = r0

    def mq_read(self):
        Rs = 0
        for i in range(0,100):
            self.get_resistance()
            Rs += self.rs
            time.sleep(0.1)
        Rs = Rs / 100
        self.rs = Rs

    def get_adjusted_r0(self, temp, hum):

        m = self.get_rsro_tempHum(temp, hum)
        n = self.get_rsro_tempHum(20, 65)
        self.r0 = self.r0 * m * n / 1000
        print("Readjusting r0", self.r0)

    def get_ppm(self, rs_ro):
            return (pow(10,((-6.900*(math.log10(rs_ro))) + 6.241)))


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
            print("Temperature: %3.1f °C" % temp)
            print("Humidity: %3.1f %% RH" % hum)
            self.temp = temp
            self.hum = hum
            return temp, hum
        else:
            print("ERR: DHT22 Sensor unavailable.")
            self.error = 'DHT22 Sensor unavailable.'
            return -1,


mq5 = MQ5()
tempSensor = DHTSensor()
#set R0
mq5.calibration()

print("Set R0: ", mq5.r0)

while True:
    if tempSensor.get_temp_hum() != -1:
        mq5.mq_read()
        mq5.get_adjusted_r0(tempSensor.temp, tempSensor.hum)
        mq5.get_corrected_ppm(tempSensor.temp, tempSensor.hum)
        print("Corrected PPM: ", mq5.ppm)
    else:
        mq5.mq_read()
        mq5.get_ppm()
        print("PPM: ", mq5.ppm)
