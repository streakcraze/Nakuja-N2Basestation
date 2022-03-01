import paho.mqtt.client as paho
import json
import pprint
import schedule
import time
from influxdb import InfluxDBClient

TIME_PERIOD = 0.1

# TODO place in utils folder
class TestPublisher:
    def __init__(self, logger):        
        self.INFLUXDB_ADDRESS = '127.0.0.1'
        self.INFLUXDB_PORT = 8086
        self.INFLUXDB_USER = 'nakuja'
        self.INFLUXDB_PASSWORD = 'C3hcAZuH6YJRqeWqH52dtHp5MjgRDT'
        self.INFLUXDB_DATABASE = 'db0'

        self.MQTT_ADDRESS = '127.0.0.1'
        self.MQTT_PORT = 1883
        self.MQTT_USER = 'nakuja'
        self.MQTT_PASSWORD = 'aVesSaVQVKjE8JCKrpTEheYERDWdfM'
        self.MQTT_CLIENT = 'publisher'
        
        self.client = None
        self.time_to_run = 0
        self.published_count = 0
        self.logger = logger
        self.setup()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code "+str(rc))

    def on_publish(self, client, userdata, msg):
        self.published_count = self.published_count + 1
        if self.published_count == 1000:
            self.published_count = 0
            self.logger.info("[{}] Published 1000 messages".format(time.ctime()))
        pass
    
    def setup(self):
        self.client = paho.Client(client_id=self.MQTT_CLIENT,clean_session=True,userdata=None,protocol=paho.MQTTv311,transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish

        self.client.username_pw_set(username=self.MQTT_USER, password=self.MQTT_PASSWORD)
        # TODO wrap connect in try except block
        self.client.connect(self.MQTT_ADDRESS, self.MQTT_PORT, 10)
        self.logger.info("CONNECTED TO MQTT")
    
    def run(self, data):
        start = time.time()
        topic = "sensorData/teststand"
        pub_data = {
            "time": time.ctime(),
            "data": float(data),
            "frequency": 1/TIME_PERIOD,
            "time_to_run": self.time_to_run
        }
        msg = json.dumps(pub_data)
        self.client.publish(topic, msg)
        end = time.time()
        self.time_to_run = end - start
