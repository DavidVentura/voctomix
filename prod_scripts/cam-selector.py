#!/usr/bin/env python3
import gi
import time
import threading
import paho.mqtt.client as mqtt
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from pyvars import *

Gst.init(None)

sources = [ 'udpsrc port=5000 ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=30 ! rtph264depay ! avdec_h264',
            'udpsrc port=5002 ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=30 ! rtph264depay ! avdec_h264',
          ]

sources = [ 'tcpclientsrc host=192.168.2.208 port=5000 ! queue ! matroskademux ! avdec_h264',
            'tcpclientsrc host=192.168.2.209 port=5000 ! queue ! matroskademux ! avdec_h264',
          ]
sources = [ 'tcpclientsrc blocksize=16384 host=192.168.2.208 port=5000 ! queue ! matroskademux ',
            'tcpclientsrc blocksize=16384 host=192.168.2.209 port=5000 ! queue ! matroskademux',
          ]

output = '''avdec_h264 ! videoconvert !
            video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1,pixel-aspect-ratio=1/1 !
            matroskamux !
            tcpclientsink blocksize=16384 host=localhost port=10001
            '''.format(WIDTH=WIDTH,HEIGHT=HEIGHT,FRAMERATE=FRAMERATE)

# output = 'videocrop left=200 right=200 ! autovideosink'
s_sources = ' ! in. '.join(sources)

s =  '{sources} ! in. input-selector name=in ! {output}'.format(output=output, sources=s_sources)
print(s)
pipeline = Gst.parse_launch(s)

pipeline.set_state(Gst.State.PLAYING)
idx = 0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("video/cam-selector")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "video/cam-selector":
        switch_camera(msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.123", 1883, 60)


def switch_camera(target):
    print(target)
    try:
        idx = int(target)
        idx -= 1
    except Exception as e:
        print(e)
        idx = 0
    idx = max(0, min(1, idx))
    switch = pipeline.get_by_name('in')
    newpad = switch.get_static_pad('sink_%d' % idx)
    switch.set_property("active-pad", newpad)
    print("Switched to %d" % idx)

print("Waiting for input on /tmp/camselectorfifo")
t = threading.Thread(target=client.loop_forever, daemon=False)
time.sleep(1)
t.start()
t.join()
pipeline.set_state(Gst.State.NULL)
