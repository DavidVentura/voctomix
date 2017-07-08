#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

gst-launch-1.0 -qe udpsrc address=239.255.42.42 port=5004 do-timestamp=true !\
	queue ! tsdemux ! queue ! h264parse ! avdec_h264 !\
	videorate ! videoscale ! videoconvert !\
	video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 !\
	queue ! matroskamux ! queue ! tcpclientsink blocksize=16384 host=localhost port=10000
echo "the stream thingy died"
