from machine import Pin, ADC
import time

while True:
    sensor_in_vcc = 5.0
    r0 = 0
    val_analog = 0
    pin = Pin(32)
    inicial_grafica = 6.5
    for i in range(0, 100):
        val = ADC(pin).read()
        val_analog += val
        time.sleep(0.1)
    sensor_avg = val_analog / 100

    sensor_volt = sensor_avg / 4095 * sensor_in_vcc  # input voltage al sensor. 4095 por el dominio de valores que retorna ADC.
    rs_air = (sensor_in_vcc-sensor_volt)/sensor_volt  # * rl que es 1kohm
    r0 = rs_air / inicial_grafica #6.5 tomado de valor inicial de la grafica del datasheet.

    print("voltaje: {}V".format(sensor_volt))
    print("r0: {}".format(r0))
    