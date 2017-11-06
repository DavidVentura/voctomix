#!/usr/bin/python3
import time
import threading
import subprocess
import paho.mqtt.client as mqtt

GRABBER_IP = '192.168.2.39'


def ping(IP):
    p = subprocess.Popen(['ping', '-c', '1', '-w', '1', IP],
                         stdout=subprocess.PIPE)
    p.communicate()
    return p.returncode == 0


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("video/mic1/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.123", 1883, 60)
t = threading.Thread(target=client.loop_forever, daemon=True)
t.start()
while t.is_alive():
    if ping(GRABBER_IP):
        print("Grabber alive")
        client.publish("video/heartbeat", "grabber")
    else:
        print("Grabber dead")
    time.sleep(10)
