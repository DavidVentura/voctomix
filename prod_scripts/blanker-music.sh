#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

echo gst-launch-1.0 -ve \
	multifilesrc location="../bg.mp3" loop=true !\
		decodebin !\
		audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=$AUDIORATE !\
		audioconvert !\
		mux. \
	\
	matroskamux name=mux !\
		tcpclientsink host=localhost port=18000
