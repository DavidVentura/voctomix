#!/usr/bin/env python3
import threading
import subprocess
import paho.mqtt.client as mqtt
import os.path
import shlex
import socket
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
modes = {
        "slides": [
            "set_stream_live",
            "set_video_a slides",
            "set_video_b cam1",
            "set_composite_mode side_by_side_preview"
         ],
        "full": [
            "set_stream_live",
            "set_video_a cam1",
            "set_composite_mode fullscreen",
            "set_audio_volume mic1 1"
        ],
        "fullslides": [
            "set_stream_live",
            "set_video_a slides",
            "set_composite_mode fullscreen",
            "set_audio_volume mic1 1",
            "set_audio_volume slides 1"
        ],
        "blank": [
            "set_stream_blank nostream",
        ]
}
ptable = {}
last_hb = time.time() * 1000
heartbeats = {}


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
        pstate = map_state()
        client.publish('mqtt_state', json.dumps({'pstate':pstate}))
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


def on_message(client, userdata, msg):
    global last_hb
    payload = msg.payload.decode('utf-8', errors='replace')
    if msg.topic == "video/heartbeat":
        send_hb = True
        ctime = time.time() * 1000
        heartbeats[payload] = ctime
        if ctime - last_hb < 8000: # If I have sent a hb in the last 8s, abort
            return
        last_hb = ctime

    data = payload
    try:
        if msg.topic != "video/heartbeat":
            data = json.loads(payload)
            print(msg.topic, data)
    except Exception as e:
        print("JSON Parse failed", payload)

    if msg.topic == "video/stop":
        key = data
        if type(key) != str:
            print(key, "is not a string!")
            return
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
            pprint(data)
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
        print("mode!", data)
        nc(data)
        # pstate['mode'] = data
    elif msg.topic == "video/exited":
        if data in ptable:
            del ptable[data]

    pstate = map_state()
    tosend = { 'pstate': pstate, 'heartbeats': heartbeats }
    client.publish('mqtt_state', json.dumps(tosend))


def map_state():
    return {k: True for k, v in ptable.items() if v is not None}
def nc(mode):
    if mode not in modes:
        print(mode, "not in modes")
        return
    hostname = 'localhost'
    port = 9999
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))
        for line in modes[mode]:
            line = "%s\n" % line
            print(line)
            s.sendall(line.encode())
            time.sleep(0.1)
        s.shutdown(socket.SHUT_WR)
        s.close()
    except Exception as e:
        print(e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.123", 1883, 60)
t_c = threading.Thread(target=client.loop_forever)
t_c.start()

print("Joining mqtt client")
t_c.join()
print("Exiting")
