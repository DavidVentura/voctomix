#!/usr/bin/env python3
import gi
import time
import threading
import paho.mqtt.client as mqtt
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
from pyvars import *



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("video/cam-selector")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    if msg.topic == "video/cam-selector":
        switch_camera(msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.123", 1883, 60)


Gst.init(None)
maincam = None
tratcam = None
def create_pipeline():
    global maincam
    global tratcam
    """
    tcpclientsrc blocksize=16384 host=192.168.2.208 port=5000 ! queue ! matroskademux ! in.
    tcpclientsrc blocksize=16384 host=192.168.2.209 port=5000 ! queue ! matroskademux ! in.
    input-selector name=in ! avdec_h264 ! videoconvert !
    video/x-raw,format=I420,width=1280,height=720,framerate=25/1,pixel-aspect-ratio=1/1 !
    matroskamux !
    tcpclientsink blocksize=16384 host=localhost port=10001
    """
    videocaps = 'video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1,pixel-aspect-ratio=1/1'.format(WIDTH=WIDTH,HEIGHT=HEIGHT,FRAMERATE=FRAMERATE)
    videocaps = 'video/x-raw,format=I420,width=1280,height=720,framerate=25/1,pixel-aspect-ratio=1/1'

    pipeline = Gst.Pipeline.new("mypipeline")
    pipeline.bus.add_signal_watch()

    main_cam = Gst.ElementFactory.make('tcpclientsrc', 'main_cam')
    main_cam.set_property("blocksize", 16384)
    main_cam.set_property("host", "192.168.2.208")
    main_cam.set_property("port", 5000)

    mcq = Gst.ElementFactory.make('queue', None)
    mcd = Gst.ElementFactory.make('matroskademux', None)

    trat_cam = Gst.ElementFactory.make('tcpclientsrc', 'trat_cam')
    trat_cam.set_property("blocksize", 16384)
    trat_cam.set_property("host", "192.168.2.209")
    trat_cam.set_property("port", 5000)

    tcq = Gst.ElementFactory.make('queue', None)
    tcd = Gst.ElementFactory.make('matroskademux', None)

    isel = Gst.ElementFactory.make('input-selector', 'isel')
    dec = Gst.ElementFactory.make('avdec_h264', None)
    vconv = Gst.ElementFactory.make('videoconvert', None)

    caps = Gst.Caps.from_string(videocaps)
    print(videocaps)
    capsfilter = Gst.ElementFactory.make("capsfilter", "filter")
    capsfilter.set_property("caps", caps)

    mux = Gst.ElementFactory.make('matroskamux', None)
    mux.set_property("streamable", True)

    sink = Gst.ElementFactory.make('tcpclientsink', None)
    sink.set_property("blocksize", 16384)
    sink.set_property("host", "localhost")
    sink.set_property("port", 10001)

    pipeline.add(main_cam)
    pipeline.add(mcq)
    pipeline.add(mcd)

    pipeline.add(trat_cam)
    pipeline.add(tcq)
    pipeline.add(tcd)

    pipeline.add(isel)
    pipeline.add(dec)
    pipeline.add(vconv)
    pipeline.add(capsfilter)
    pipeline.add(mux)
    pipeline.add(sink)
    
    tpl = isel.get_pad_template("sink_%u")
    maincam = isel.request_pad(tpl, "sink_%u", None)
    tratcam = isel.request_pad(tpl, "sink_%u", None)

    mcd.connect('pad-added', c_d_src_c(maincam))
    tcd.connect('pad-added', c_d_src_c(tratcam))

    main_cam.link(mcq)
    mcq.link(mcd)
    # dynamically linked

    trat_cam.link(tcq)
    tcq.link(tcd)
    # dynamically linked

    isel.link(dec)
    dec.link(vconv)
    vconv.link(capsfilter)
    capsfilter.link(mux)
    mux.link(sink)

    return pipeline


def c_d_src_c(target):
    def decode_src_created(element, pad):
        pad.link(target)
    return decode_src_created

def switch_camera(target):
    try:
        idx = int(target)
        idx -= 1
    except Exception as e:
        print(e)
        idx = 0
    idx = max(0, min(1, idx))
    switch = pipeline.get_by_name('isel')
    # newpad = switch.get_static_pad('sink_%d' % idx)
    # switch.set_property("active-pad", newpad)
    if idx == 0:
        switch.set_property("active-pad", maincam)
    if idx == 1:
        switch.set_property("active-pad", tratcam)
    print("Switched to %d" % idx)

t = threading.Thread(target=client.loop_forever, daemon=False)
time.sleep(1)
t.start()


mainloop = GObject.MainLoop()
pipeline = create_pipeline()
print("Pipeline created")
pipeline.set_state(Gst.State.PLAYING)

try:
    mainloop.run()
except KeyboardInterrupt:
    print("Interrupted!")
    pipeline.set_state(Gst.State.NULL)
    mainloop.quit()
    client.disconnect()
    print("Disconnected")

if t.is_alive():
    t.join()
