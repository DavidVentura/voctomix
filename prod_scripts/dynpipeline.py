#!/usr/bin/python3
import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import time
import threading
import os
import stat

def quit():
    pipeline.send_event(Gst.Event.new_eos())

def set_kv(n, k, v):
        el = pipeline.get_by_name(n)
        if el is None:
            print("No such element %s" % n)
            return

        el.set_state(Gst.State.PAUSED)
        pipeline.set_state(Gst.State.PAUSED)

        el.set_property(k, int(v))

        el.set_state(Gst.State.PLAYING)
        pipeline.set_state(Gst.State.PLAYING)

        print("Succesfully set %s.%s = %s" % ( n, k, v ) )

def parse_message(line):
        if "=" not in line or ";" not in line:
            print("Invalid line. Needs ; and =")
            return
        name = line.split(";")[0]

        line = line.split(";")[1]
        key = line.split("=")[0]
        val = line.split("=")[1]
        
        set_kv(name, key, val)

def control():
    FIFO="/tmp/fifo"
    if os.path.exists(FIFO):
        if stat.S_ISFIFO(os.stat(FIFO).st_mode):
            pass
        else:
            os.remove(FIFO)
            os.mkfifo(FIFO)
    else:
        os.mkfifo(FIFO)

    while True:
        with open(FIFO) as fifo:
            line=fifo.read().strip()
            print("Got: ", line)
            parse_message(line)


if __name__ == "__main__":
    # initialization
    Gst.init(None)

    p = """
    udpsrc port=5002 do-timestamp=true name=src ! queue ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=50 ! rtph264depay ! avdec_h264 !
        videoconvert !
        video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1,pixel-aspect-ratio=1/1 !
        mux.
    matroskamux name=mux !
        tcpclientsink host=localhost port=10001
        """.format(WIDTH=1280, HEIGHT=720, FRAMERATE=25)

    p = """
	udpsrc port=5003 !
		audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate={AUDIORATE} !
		audioconvert !
		queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=400000000 name=delay !
                volume volume=1.2 !
		mux.
	matroskamux name=mux !
		tcpclientsink host=localhost port=10003
    """.format(AUDIORATE=48000)

    pipeline = Gst.parse_launch (p)
    if pipeline == None:
        print ("Failed to create pipeline")
        sys.exit(0)

    el = pipeline.get_by_name("delay")
    help(el)
    # run
    pipeline.set_state(Gst.State.PLAYING)
    t = threading.Thread(target=control, daemon=True)
    t.start()
    while True:
        time.sleep(10000)

    # cleanup
    pipeline.set_state(Gst.State.NULL)

