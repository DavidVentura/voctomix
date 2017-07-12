#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

AUDIOSRC='audiotestsrc freq=400 volume=0'
AUDIOSRC='d. ! queue ! mpegaudioparse ! avdec_mp3 ! queue' 
WITH_AUDIO=""
gst-launch-1.0 -qe \
    udpsrc address=239.255.42.42 port=5004 do-timestamp=true ! queue !\
    tsdemux name=d !\
    queue ! h264parse ! avdec_h264 !\
	videorate ! videoscale add-borders=false ! videoconvert !\
	video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 !\
    matroskamux name=m ! queue ! tcpclientsink blocksize=16384 host=localhost port=10000
    #queue ! audioconvert ! audioresample ! audiorate ! \


    #
	#m. $AUDIOSRC !\
    #audioconvert ! audioresample ! audiorate!\
    #audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=$AUDIORATE !\
