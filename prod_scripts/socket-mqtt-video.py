#!/usr/bin/env python3
import threading
import subprocess
import paho.mqtt.client as mqtt
import os.path
import shlex
import json
import time
from pprint import pprint
BASEDIR = '/home/nginx/voctomix/prod_scripts/'
pmap = {
        "r_slides": ['./slides2.sh'],
        "r_slides_bg": ['./bg-with-text.sh'],
        "r_cams": ['./cam-selector.py'],
        "r_blank_v": ['./blanker.py'],
        "r_blank_m": ['./source-nostream-music-from-folder.py', '/home/nginx/voctomix/'],
        "r_blank_t": ['./timer.py'],
        "p_stream": ['./stream-sd.sh']
        }
ptable = {}


def popenAndCall(key, args):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that
    would give to subprocess.Popen.
    """
    def runInThread(key, args):
        popenArgs = list(pmap[key])  # avoid modifying pmap
        popenArgs.extend(args)
        print(key, args, popenArgs)
        proc = subprocess.Popen(popenArgs, cwd=BASEDIR)
        ptable[key] = proc
        proc.wait()
        if key in ptable:
            del ptable[key]
    thread = threading.Thread(target=runInThread, args=(key, args))
    thread.start()
    # returns immediately after the thread starts
    return thread


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("video/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "video/heartbeat":
        # FIXME
        return

    payload = msg.payload.decode('utf-8', errors='replace')
    try:
        data = json.loads(payload)
    except Exception as e:
        print("JSON Parse failed", payload)
        return

    print(msg.topic, data)
    if msg.topic == "video/stop":
        key = data
        if key not in ptable:
            print("Process %s not running(2)!" % key)
            pprint(ptable)
            return

        ptable[key].terminate()  # kill the process
        time.sleep(0.1)
        if key in ptable and ptable[key] is not None and ptable[key].poll() is not None:
            # did the process REALLY die?
            del ptable[key]

    if msg.topic == "video/launch":
        # example payload:
        # r_slides_bg PEFE - Abordaje Cosmiátrico
        if 'key' not in data:
            print("No key in data")
            return
        key = data['key']
        print("Launch key:", key)
        if key not in pmap:
            print("%s not in pmap" % key)
            pprint(pmap)
            return

        if key in ptable:
            print("Process %s already running!" % key)
            return

        if 'args' in data:
            args = data['args']
        else:
            args = []
        print("Calling popen with args = ", args)
        popenAndCall(key, args)
    elif msg.topic == "video/mode":
        print("mode!")
        nc(data)
        # pstate['mode'] = data
    elif msg.topic == "video/exited":
        if data in ptable:
            del ptable[data]

    pstate = {k: True for k, v in ptable.items() if v is not None}
    client.publish('mqtt_state', json.dumps(pstate))
    pprint(pstate)
    print("#"*50)


def nc(mode):
    pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.123", 1883, 60)
t_c = threading.Thread(target=client.loop_forever)
t_c.start()

print("Joining mqtt client")
t_c.join()
print("Exiting")
