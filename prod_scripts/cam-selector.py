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
sources = [ 'tcpclientsrc host=192.168.2.208 port=5000 ! queue ! matroskademux ',
            'tcpclientsrc host=192.168.2.209 port=5000 ! queue ! matroskademux',
          ]

output = '''avdec_h264 ! videoconvert !
            video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1,pixel-aspect-ratio=1/1 !
            matroskamux !
            tcpclientsink host=localhost port=10001
            '''.format(WIDTH=WIDTH,HEIGHT=HEIGHT,FRAMERATE=FRAMERATE)

# output = 'videocrop left=200 right=200 ! autovideosink'
s_sources = ' ! in. '.join(sources)

s =  '{sources} ! in. input-selector name=in ! {output}'.format(output=output, sources=s_sources)
print(s)
pipeline = Gst.parse_launch(s)

pipeline.set_state(Gst.State.PLAYING)
idx = 0

while True:
    print("Waiting for input")
    i = input()
    if i == "2":
        idx = 1
    elif i == "1":
        idx = 0
    else:
        print("Invalid input")
        continue
    switch = pipeline.get_by_name('in')
    newpad = switch.get_static_pad('sink_%d' % idx)
    switch.set_property("active-pad", newpad)
    print("Switched to %d" % idx)

pipeline.set_state(Gst.State.NULL)
