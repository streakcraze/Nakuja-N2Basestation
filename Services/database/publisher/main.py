import paho.mqtt.client as paho
import json
import schedule
import time

broker = "127.0.0.1"
port = 1883


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test")


def on_publish(client, userdata, msg):
    # print(f"Published msg: {msg}")
    pass

client = paho.Client(client_id="publisher",clean_session=True,userdata=None,protocol=paho.MQTTv311,transport="tcp")
client.on_connect = on_connect
client.on_publish = on_publish

client.username_pw_set(username="nakuja",password="aVesSaVQVKjE8JCKrpTEheYERDWdfM")
print("Connecting...")
client.connect("0.0.0.0", 1883, 10)

counter = 0
def job():
    global counter 
    data = 120 + counter
    topic = f"sensorData/teststand"
    pub_data = {
        "time": time.localtime(),
        "data": data,
    }
    msg = json.dumps(pub_data)
    client.publish(topic, msg)
    counter = counter + 1
    if counter == 10:
        counter = 0
    print(counter)


schedule.every(0.01).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(0.01)