#!/usr/bin/env python3
import gi
import time
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

sources = [ 'udpsrc port=5000 ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=30 ! rtph264depay ! avdec_h264',
            'udpsrc port=5002 ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=30 ! rtph264depay ! avdec_h264',
          ]

output = '''videoconvert !
            video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1,pixel-aspect-ratio=1/1 !
            mux.
            matroskamux name=mux !
            tcpclientsink host=localhost port=10001
            '''.format(WIDTH=1280,HEIGHT=720,FRAMERATE=25)

# output = 'videocrop left=200 right=200 ! autovideosink'
s_sources = ' ! in. '.join(sources)

s =  '{sources} ! in. input-selector name=in ! {output}'.format(output=output, sources=s_sources)
print(s)
pipeline = Gst.parse_launch(s)

pipeline.set_state(Gst.State.PLAYING)
idx = 0

while True:
    input()
    idx = (idx + 1) % len(sources)
    switch = pipeline.get_by_name('in')
    newpad = switch.get_static_pad('sink_%d' % idx)
    switch.set_property("active-pad", newpad)
    print("Switched to %d" % idx)

pipeline.set_state(Gst.State.NULL)
