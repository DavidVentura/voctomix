#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

while [ true ]; do
	gst-launch-1.0 -qe tcpclientsrc host=192.168.2.208 port=5002 !\
		matroskademux ! h264parse ! avdec_h264 !\
		videorate ! videoscale add-borders=false ! videoconvert !\
		video/x-raw,format=I420,width=1280,height=720,framerate=25/1,pixel-aspect-ratio=1/1 !\
		matroskamux ! tcpclientsink host=localhost port=10000

	echo "the stream thingy died"
	sleep 1
done
