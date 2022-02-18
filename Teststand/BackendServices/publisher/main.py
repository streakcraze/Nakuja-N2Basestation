import paho.mqtt.client as paho
import json
import schedule
import time
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '127.0.0.1'
INFLUXDB_USER = ''
INFLUXDB_PASSWORD = ''
INFLUXDB_DATABASE = 'telegraf'

broker = "127.0.0.1"
port = 1883
counter = 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test")


def on_publish(client, userdata, msg):
    # print(f"Published msg: {msg}")
    pass


influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

databases = influxdb_client.get_list_database()
if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
    influxdb_client.create_database(INFLUXDB_DATABASE)
influxdb_client.switch_database(INFLUXDB_DATABASE)

client = paho.Client(client_id="Demo",clean_session=True,userdata=None,protocol=paho.MQTTv311,transport="tcp")
client.on_connect = on_connect
client.on_publish = on_publish

client.username_pw_set(username="",password="")
print("Connecting...")
client.connect("127.0.0.1", 1883, 10)

def job():
    global counter
    if counter == 99:
        counter = 0
    with open("generated.json") as f:
        data = json.load(f)
    for i in range(len(data)):
        patient_name = data[i]['name'].replace(" ", "_")
        age = data[i]['age']
        chestcondition = data[i]['chestcondition']
        bloodoxygen = data[i]['bloodoxygen'][counter]['val']
        bodytemperature = data[i]['bodytemperature'][counter]['val']
        bpm = data[i]['bpm'][counter]['val']
        breathingrate = data[i]['breathingrate'][counter]['val']
        topic = f"sensorData/{patient_name}"
        pub_data = {
            "chestcondition": chestcondition,
            "bloodoxygen": bloodoxygen,
            "bodytemperature": bodytemperature,
            "bpm": bpm,
            "breathingrate": breathingrate
        }
        json_body = [pub_data]
        # ret = influxdb_client.write_points(json_body)

    counter = counter + 1
    print(f"counter: {counter}")

    

schedule.every(300).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)