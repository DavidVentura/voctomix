#!/usr/bin/env python3
import gi
import time
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

def control():
     FIFO="/tmp/camselectorfifo"
     if os.path.exists(FIFO):
          if not stat.S_ISFIFO(os.stat(FIFO).st_mode):
               os.remove(FIFO)
               os.mkfifo(FIFO)
     else:
          os.mkfifo(FIFO)

     while True:
        with open(FIFO) as fifo:
            line=fifo.read().strip()
            print("Got: ", line)
            if "=" not in line:
                 print("Invalid line.")
                 continue
            val = line.strip()
            if val == "2":
                switch_camera(val)


def switch_camera(target):
    try:
        idx = int(target)
        idx -= 1
    except:
        idx = 0
    idx = max(0, min(1, idx))
    switch = pipeline.get_by_name('in')
    newpad = switch.get_static_pad('sink_%d' % idx)
    switch.set_property("active-pad", newpad)
    print("Switched to %d" % idx)

print("Waiting for input on /tmp/camselectorfifo")
t = threading.Thread(target=control, daemon=False)
time.sleep(1)
t.start()
t.join()
pipeline.set_state(Gst.State.NULL)
