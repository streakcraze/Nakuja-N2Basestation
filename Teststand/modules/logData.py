import paho.mqtt.client as paho
import json
import schedule
import time
from influxdb import InfluxDBClient


class Publish:
    def __init__(self):
        self.broker = "127.0.0.1"
        self.port = 1883
        self.counter = 0
        self.client = paho.Client(client_id="Demo",clean_session=True,userdata=None,protocol=paho.MQTTv311,transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish

        self.client.username_pw_set(username="",password="")
        self.client.connect(self.broker, self.port, 10)

    def on_connect(self, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("test")


    def on_publish(self, userdata, msg):
        # print(f"Published msg: {msg}")
        pass

    def publish(self, data):
        topic = f"sensorData/test"
        pub_data = {
            "data": data,
        }
        json_body = [pub_data]
        self.client.publish(topic, json_body)
