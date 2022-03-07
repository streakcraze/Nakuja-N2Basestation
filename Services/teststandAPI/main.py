import paho.mqtt.client as paho
import json
import time
import os

# TODO place in utils flder
class Publisher:
    def __init__(self, logger):        
        self.MQTT_ADDRESS = '127.0.0.1'
        self.MQTT_PORT = 1883
        self.MQTT_USER = 'nakuja'
        self.MQTT_PASSWORD = 'aVesSaVQVKjE8JCKrpTEheYERDWdfM'
        self.MQTT_CLIENT = 'teststandapi'
        
        self.client = None
        self.logger = logger
        self.setup()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code "+str(rc))
    
    def on_publish(self, client, userdata, message):
        self.logger.info("Published message : {}".format(message))
    
    def setup(self):
        self.client = paho.Client(client_id=self.MQTT_CLIENT,clean_session=True,userdata=None,protocol=paho.MQTTv311,transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.username_pw_set(username=self.MQTT_USER, password=self.MQTT_PASSWORD)
        self.client.connect(self.MQTT_ADDRESS, self.MQTT_PORT, 10)
        self.logger.info("CONNECTED TO MQTT")
        # self.loggingthread = threading.Thread(target=self.check_logging)
        # self.loggingthread.setDaemon(True)
        # self.client.loop_forever()
    
    def publish(self, data):
        topic = "sensorData/internals"
        pub_data = {
            "time": time.ctime(),
            "data": data,
        }
        msg = json.dumps(pub_data)
        print(msg)
        self.client.publish(topic, msg)

class Operation:
    def __init__(self, logger):
        self.ignition = False
        self.logging = False
        self.publisher = Publisher(logger)
        self.logger = logger

    def startignition(self):
        if self.ignition == False:
            if self.logging == False:
                response = {"error": "Start logging first", "redirect": "/api/start_logging"}
            else:
                self.ignition = True
                response = {"action": "Started ignition", "ignition status": str(self.ignition)}
                self.logger.info("Started ignition")
                self.publisher.publish(data=response)
        else:
            response = {"action": "Ignition already started", "ignition status": str(self.ignition)}
        return response

    def stopignition(self):
        if self.ignition == True:
            self.ignition = False
            response = {"action": "Stopped ignition", "ignition status": str(self.ignition)}
            self.logger.info("Stopped ignition")
            self.publisher.publish(data=response)
        else:
            response = {"action": "Ignition already stopped", "ignition status": str(self.ignition)}
        return response

    def startlogging(self):
        if self.logging == False:
            self.logging = True
            response = {"action": "Started logging", "logging status": str(self.logging)}
            self.logger.info("Started logging")
            self.publisher.publish(data=response)
        else:
            response = {"action": "Logging already started", "logging status": str(self.logging)}
        return response

    def stoplogging(self):
        if self.logging == True:
            self.logging = False
            response = {"action": "Stopped logging", "logging status": str(self.logging)}
            self.logger.info("Stopped logging")
            self.publisher.publish(data=response)
        else:
            response = {"action": "Logging already stopped", "logging status": str(self.logging)}
        return response
