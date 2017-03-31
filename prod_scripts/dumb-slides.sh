#!/bin/sh
confdir="`dirname "$0"`/"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

while [ true ]; do
	nc -l -p 5001 | ffmpeg -loglevel error -y -nostdin -xerror -hide_banner \
		-use_wallclock_as_timestamps 1 \
		-f h264 -probesize 32 -analyzeduration 1000 -i - \
		-filter_complex "[0:v] scale=$WIDTH:$HEIGHT,fps=$FRAMERATE [v]" \
		-map "[v]"\
		-c:v rawvideo \
		-pix_fmt yuv420p \
		-f matroska \
		tcp://localhost:10000

	echo $?
	echo "the stream thingy died"
	sleep 1
done
