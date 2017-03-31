#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

#IN = 1280x720
PORT=5000
if [ $# -eq 1 ]; then
    if [ $1 -eq 2 ]; then
        PORT=5002
        echo "Using cam2"
    fi
fi


gst-launch-1.0 -qe \
	udpsrc port=$PORT do-timestamp=true ! queue ! application/x-rtp, payload=96 ! rtpjitterbuffer latency=50 ! rtph264depay ! avdec_h264 ! \
		videoconvert !\
		video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 ! \
		mux. \
	matroskamux name=mux !\
		tcpclientsink host=localhost port=10001
