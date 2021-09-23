from machine import Pin, SoftI2C
class GroveSensor:
    DEFAULT_I2C_ADDR = 0x04
    ADDR_IS_SET = 0  # if this is the first time to run, if 1126, set
    ADDR_FACTORY_ADC_NH3 = 2
    ADDR_FACTORY_ADC_CO = 4
    ADDR_FACTORY_ADC_NO2 = 6

    ADDR_USER_ADC_HN3 = 8
    ADDR_USER_ADC_CO = 10
    ADDR_USER_ADC_NO2 = 12
    ADDR_IF_CALI = 14  # IF USER HAD CALI

    ADDR_I2C_ADDRESS = 20

    CH_VALUE_NH3 = 1
    CH_VALUE_CO = 2
    CH_VALUE_NO2 = 3

    CMD_ADC_RES0 = 1  # NH3
    CMD_ADC_RES1 = 2  # CO
    CMD_ADC_RES2 = 3  # NO2
    CMD_ADC_RESALL = 4  # ALL CHANNEL
    CMD_CHANGE_I2C = 5  # CHANGE I2C
    CMD_READ_EEPROM = 6  # READ EEPROM VALUE, RETURN UNSIGNED INT
    CMD_SET_R0_ADC = 7  # SET R0 ADC VALUE
    CMD_GET_R0_ADC = 8  # GET R0 ADC VALUE
    CMD_GET_R0_ADC_FACTORY = 9  # GET FACTORY R0 ADC VALUE
    CMD_CONTROL_LED = 10
    CMD_CONTROL_PWR = 11

    CO = 0
    NO2 = 1
    NH3 = 2
    C3H8 = 3
    C4H10 = 4
    CH4 = 5
    H2 = 6
    C2H5OH = 7

    adcValueR0_NH3_Buf = 0
    adcValueR0_C0_Buf = 0
    adcValueR0_NO2_Buf = 0


    def __init__(self):
        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
        self.scan()
    
    def scan(self):
        x = self.i2c.scan()

        if len(x) == 0:
            print("No Groove device found!")
            return -1
        else: 
            for device in x:
                print("Groove Adr", device, "Hex", hex(device))

    
    def cmd(self, cmd, nbytes=2):
        self.i2c.writeto(self.addr, bytes(cmd))
        dta = 0
        raw = self.i2c.readfrom(self.addr, nbytes)
        for byte in raw:
            dta = dta * 256 + int(byte)

        if cmd == self.CH_VALUE_NH3:
            if dta > 0:
                self.adcValueR0_NH3_Buf = dta
            else:
                dta = self.adcValueR0_NH3_Buf
        elif cmd == self.CH_VALUE_CO:
            if dta > 0:
                self.adcValueR0_CO_Buf = dta
            else:
                dta = self.adcValueR0_CO_Buf
        elif cmd == self.CH_VALUE_NO2:
            if dta > 0:
                self.adcValueR0_NO2_Buf = dta
            else:
                dta = self.adcValueR0_NO2_Buf

        return dta

    def calc_gas(self, gas):

        A0_0 = self.cmd([6, self.ADDR_USER_ADC_HN3])
        A0_1 = self.cmd([6, self.ADDR_USER_ADC_CO])
        A0_2 = self.cmd([6, self.ADDR_USER_ADC_NO2])

        An_0 = self.cmd([self.CH_VALUE_NH3])
        An_1 = self.cmd([self.CH_VALUE_CO])
        An_2 = self.cmd([self.CH_VALUE_NO2])

        ratio0 = An_0 / A0_0 * (4095 - A0_0) / (4095 - An_0)
        ratio1 = An_1 / A0_1 * (4095 - A0_1) / (4095 - An_1)
        ratio2 = An_2 / A0_2 * (4095 - A0_2) / (4095 - An_2)

        c = 0.0

        if gas == self.CO:
            c = pow(ratio1, -1.179) * 4.385

        elif gas == self.NO2:
            c = pow(ratio2, 1.007) / 6.855
        elif gas == self.NH3:
            c = pow(ratio0, -1.67) / 1.47
        elif gas == self.C3H8:
            c = pow(ratio0, -2.518) * 570.164
        elif gas == self.C4H10:
            c = pow(ratio0, -2.138) * 398.107
        elif gas == self.CH4:
            c = pow(ratio1, -4.363) * 630.957
        elif gas == self.H2:
            c = pow(ratio1, -1.8) * 0.73
        elif gas == self.C2H5OH:
            c = pow(ratio1, -1.552) * 1.622

        return c or -3

    def power_on(self):
        self.cmd([self.CMD_CONTROL_PWR, 1])
