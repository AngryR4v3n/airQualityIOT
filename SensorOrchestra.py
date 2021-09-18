from mq131 import MQ131
from mq5 import MQ5, DHTSensor
import network
import ntptime
import time
from machine import RTC


rtc = RTC()
def createFile():
    try:
        f=open('logs.csv', 'r')
        print('logs.csv'+ ' already exists!')
        return 1
    except Exception:
        print("creating filename: ", "logs.csv")
        f=open("logs.csv", 'w')
        #header
        f.write("TIMESTAMP,CO,O3,TEMPERATURE,HUMIDITY")
        f.write('\n')
        f.close()
    return 0

def connectWifi():
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        wifi.active(True)
        wifi.connect("TIGO-A0AD", "molinajimenez")
        time.sleep(6)
        if wifi.isconnected():
            print("Connected to Internet!")
        else:
            print("Wifi error")

        
    print("Local time:%s" %str(time.localtime()))
    







print("Setting up everything!")
mq5 = MQ5()
tempSensor = DHTSensor()
mq131 = MQ131()
#set R0
mq5.get_resistance()
tempSensor.get_temp_hum()
print("Initial temp", tempSensor.temp, tempSensor.hum)
mq5.get_corrected_r0(tempSensor.temp, tempSensor.hum)
print("SET R0 for MQ5", mq5.r0)

createFile()
connectWifi()
f = open('logs.csv', "a")
count = 0
while True:
    
    if tempSensor.get_temp_hum() != -1:
        mq5.get_resistance()
        mq5.get_corrected_ppm(tempSensor.temp, tempSensor.hum)
        print("Corrected CO PPM: ", mq5.ppm)

    else:
        mq5.get_resistance()
        mq5.get_ppm()
        print("CO PPM: ", mq5.ppm)

    mq131.read()
    print("O3 PPM", mq131.ppm)
    # YYYY-MM-DD HH:MM
    if rtc.datetime()[5] < 10:
        timestamp = str(rtc.datetime()[0]) + '-' + str(rtc.datetime()[1]) + '-' +  str(rtc.datetime()[2]) + ' ' + str(rtc.datetime()[4]) + ':' + "0" + str(rtc.datetime()[5])
    else:
        timestamp = str(rtc.datetime()[0]) + '-' + str(rtc.datetime()[1]) + '-' +  str(rtc.datetime()[2]) + ' ' + str(rtc.datetime()[4]) + ':' + str(rtc.datetime()[5])
    print(timestamp)
    line = timestamp + ',' + str(mq5.ppm) + ',' + str(mq131.ppm) + ',' + str(tempSensor.temp) + ',' + str(tempSensor.hum)
    f.write(line)
    f.write('\n')
    
    if count > 150:
        f.close()
    else:
        count += 1
    time.sleep(5)
