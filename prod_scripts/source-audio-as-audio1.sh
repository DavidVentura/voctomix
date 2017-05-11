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
HOST='192.168.2.79'

gst-launch-1.0 -qe \
	tcpclientsrc host=$HOST port=5000 do-timestamp=true ! queue ! matroskaparse ! matroskademux ! queue ! opusdec $DELAY ! \
	queue ! matroskamux streamable=true !\
		tcpclientsink host=localhost port=10003
