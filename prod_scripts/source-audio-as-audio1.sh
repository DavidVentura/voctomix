#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

#FIXME: Python script so this delay is configurable
DELAY="! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=2400000000"
DELAY="! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=1400000000"
DELAY="! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=0400000000"
DELAY=""

gst-launch-1.0 -qe \
	udpsrc port=5003 ! \
		audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=$AUDIORATE !\
		audioconvert $DELAY !\
		mux. \
	\
	matroskamux name=mux !\
		tcpclientsink host=localhost port=10003
