from machine import Pin, SoftI2C


class MQ131:
    def __init__(self):
        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
        self.memAdr = 80 #"0x50" en hex.
        self.RO_LIMPIO = 9748.603
        self.RL_VALUE = 10000 #segun medido
        self.ppm = 0
        self.adc = 0
        self.rs = 0
        self.r0 = 0

        #curvas log log
        self.paramA = 6.747188
        self.paramB = 2.451821

        #curvas temp humid
        #30%
        self.pointsH1 = [1.7026, 1.5815, 1.4251, 1.2483, 1.1476, 1.0037, 0.868]

        #80%
        self.pointsH2 = [1.2565, 1.1722, 1.0489, 0.9276, 0.8536, 0.7446, 0.6419]

        self.x_points = [-10, 0, 10, 20, 30, 40, 50]

        self.scan()
    
    def scan(self):
        x = self.i2c.scan()

        if len(x) == 0:
            print('No device!')
            return -1
            
        else: 
            for device in x:
                print("Addr", device, "Hex", hex(device))

            self.memAdr = device

    def read(self):
        #conversion
        x = self.i2c.readfrom_mem(0x50, 0x00, 2)
        num = int.from_bytes(x, "big")
        self.adc = num

    def resistance(self):
         self.rs = ((4096 * self.RL_VALUE) / self.adc) - self.RL_VALUE

    def get_r0(self):
        self.r0 = self.rs * pow((self.paramA / 0.01), 1/self.paramB)
        return self.r0


    def get_temp_hum_gain(self, temp, hum):
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

    def get_ppm(self):
            self.ppm = self.paramA * pow((self.rs/self.r0), self.paramB)

    def get_corrected_ppm(self, temp, hum):
        t = self.get_temp_hum_gain(temp, hum)

        #referencia segun documentacion.
        q = self.get_temp_hum_gain(20,65)
        res = self.rs * (q/t)
        self.rs = res
        self.get_ppm()
