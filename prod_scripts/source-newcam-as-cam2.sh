#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

#IN = 1280x720

gst-launch-1.0 \
	udpsrc port=5002 do-timestamp=true ! queue ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=50 ! rtph264depay ! avdec_h264 ! \
		videoconvert ! videoscale add-borders=false !\
		video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 ! \
		mux. \
	matroskamux name=mux !\
		tcpclientsink host=localhost port=10002
