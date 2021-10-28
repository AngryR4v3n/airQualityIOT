import time
from util import create_mqtt_client, get_telemetry_topic, get_c2d_topic, parse_connection

#Constantes, no cambiar.
HOST_NAME = "HostName"
SHARED_ACCESS_KEY_NAME = "SharedAccessKeyName"
SHARED_ACCESS_KEY = "SharedAccessKey"
SHARED_ACCESS_SIGNATURE = "SharedAccessSignature"
DEVICE_ID = "DeviceId"
MODULE_ID = "ModuleId"
GATEWAY_HOST_NAME = "GatewayHostName"


#Ciclo de vida -> Configure Vars, configure_mqtt, connect, callback_handler, subscribe_topic, telemetry_topic, y send. 
class Azure:
    def __init__(self):
        self.dict_keys = parse_connection("HostName=hau-iot-hub.azure-devices.net;DeviceId=station;SharedAccessKey=49MVnJo7+2m5pli2eoLvPDmBlFzlVe+68PpO0duzITc=")
        self.configure_vars()
        ## Create you own shared access signature from the connection string that you have
        ## Azure IoT Explorer can be used for this purpose.
        self.sas_token_str = "SharedAccessSignature sr=hau-iot-hub.azure-devices.net%2Fdevices%2Fstation&sig=XbXuliRprvlzOmB%2ByiqgxadFcd3h%2BKIJlY%2BeSbVCBVM%3D&se=1636031194"
        
    def configure_vars(self):
        ## Parse the connection string into constituent parts
        self.shared_access_key = self.dict_keys.get(SHARED_ACCESS_KEY)
        self.shared_access_key_name =  self.dict_keys.get(SHARED_ACCESS_KEY_NAME)
        self.gateway_hostname = self.dict_keys.get(GATEWAY_HOST_NAME)
        self.hostname = self.dict_keys.get(HOST_NAME)
        self.device_id = self.dict_keys.get(DEVICE_ID)
        self.module_id = self.dict_keys.get(MODULE_ID)
        ## Create username following the below format '<HOSTNAME>/<DEVICE_ID>'
        self.username = self.hostname + '/' + self.device_id

    def configure_mqtt(self):
        ## Create UMQTT ROBUST or UMQTT SIMPLE CLIENT
        self.mqtt_client = create_mqtt_client(client_id=self.device_id, hostname=self.hostname, username=self.username, password=self.sas_token_str, port=8883, keepalive=120, ssl=True)

    def connect(self):
        print("Connecting to Azure...")
        self.mqtt_client.reconnect()


    def callback_handler(self,topic, message_receive):
        print("Received message from Azure:")
        print(message_receive)

    def subscribe_topic(self):
        self.subscribe_topic = get_c2d_topic(self.device_id)
    
        self.mqtt_client.set_callback(self.callback_handler)
        self.mqtt_client.subscribe(topic=self.subscribe_topic)

        
    def telemetry_topic(self):
        self.topic = get_telemetry_topic(self.device_id)

    
    def send(self, toSend):
        ## Send telemetry
        print("Sending message....")
        print(toSend)
        self.mqtt_client.publish(topic=self.topic, msg=toSend)
 
    def wait(self):
        ## Send a C2D message and wait for it to arrive at the device
        print("waiting for message")
        self.mqtt_client.wait_msg()
