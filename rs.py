from machine import Pin, ADC
import time

while True:
    ratio = 0
    pin = Pin(32)
    sensorValue = ADC(pin).read()
    print("raw val",sensorValue)
    sensor_volt = (sensorValue / 4095) * 5
    rs_gas = (5 - sensor_volt) / sensor_volt

    ratio = rs_gas / 0.885

    print("sensor_volt ", sensor_volt)
    print("RS_ratio ", rs_gas)
    print("RS/R0", ratio)

    time.sleep(0.5)
