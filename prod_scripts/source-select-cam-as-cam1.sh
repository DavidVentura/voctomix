#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

#IN = 1280x720
HOST="192.168.2.208"
if [ $# -eq 1 ]; then
    if [ $1 -eq 2 ]; then
		HOST="192.168.2.209"
        echo "Using cam2"
    fi
fi


gst-launch-1.0 -qe \
	tcpclientsrc host=$HOST port=5000 do-timestamp=true ! queue ! matroskademux ! avdec_h264 ! \
		videoconvert !\
		video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 ! \
		mux. \
	matroskamux name=mux !\
		tcpclientsink host=localhost port=10001