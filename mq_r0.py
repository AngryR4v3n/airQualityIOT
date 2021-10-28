from machine import Pin, ADC
import time

PARAMA = 933110825
PARAMB = -14.10743
RL_VALUE = 1000
#asumimos 1 ppm ..
PPM = 1
R0 = 2800
def get_res():
    valor = ADC(Pin(32)).read()
    res = ((4096 * RL_VALUE) / valor) - RL_VALUE
    return res
    
def createFile():
    f=open("r0_record", 'w')
def get_ppm(rsr0):
    return PARAMA * pow(rsr0, PARAMB)

createFile()
while True: 
    resis = get_res()
    print("resis", resis)
    time.sleep(1)