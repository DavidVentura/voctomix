#!/usr/bin/env python3
import json
import os
import signal
import socket
import subprocess
import sys
import time
import threading
import websocket
import paho.mqtt.client as mqtt


class wstomqtt():
    ws = None
    ip = "ws://192.168.2.208:9001"

    def __init__(self):
        print('asd')
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.t = threading.Thread(target=self.client.loop_forever, daemon=True)
        self.t.start()
        self.client.connect("192.168.2.123", 1883, 60)

        self.conn(self.ip)
        while True:
            try:
                data = self.ws.recv()
            except Exception as e:
                print(e)
                self.conn(self.ip)
                continue
            try:
                j = json.loads(data)
            except Exception as e:
                print(e)
                print("Invalid json?")
                continue
            if 'type' in j and j['type'] in ['snowmix', 'mqtt_state']:
                continue
            print("← ws>", j)
            if 'type' not in j:
                continue
            if j['type'] != 'mqtt':
                continue
            if 'topic' not in j or 'payload' not in j:
                continue

            payload = json.dumps(j['payload'])
            print("Publish payload", payload)
            self.client.publish(j['topic'], payload)


    def send(self, data):
        try:
            if type(data) is dict:
                data = json.dumps(data)
            print("→ ws>", data)
            self.ws.send(data)
        except Exception as e:
            print(e)

    def conn(self, target, timeout=None):
        if self.ws is None:
            self.ws = websocket.WebSocket()
        try:
            self.ws.connect(target)
        except Exception as e:
            print(e)
            if timeout is None:
                timeout = 2
            timeout = min(timeout, 90)
            time.sleep(timeout)
            self.conn(target, timeout+2) #keep trying you basterd

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("mqtt_state/#")
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("mqtt>", msg.topic, str(msg.payload))
        if msg.topic == 'mqtt_state': 
            self.send({'type': 'mqtt_state', 'payload': msg.payload.decode('utf-8', errors='replace')})

if __name__ == '__main__':
    w = wstomqtt()
