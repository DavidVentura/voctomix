#!/bin/sh
MAXRATE=1100
MAXRATE=600
MAXRATE=900
MAXRATE=1000
ffmpeg -y -nostdin -hide_banner -loglevel warning -stats \
	-i tcp://localhost:15000 \
	-threads:0 3 \
	-aspect 16:9 \
	-c:v libx264 \
	-maxrate "${MAXRATE}k" -bufsize:v:0 2048k -qmin 21 \
	-pix_fmt:0 yuv420p -profile:v:0 high -g:v:0 50 \
	-preset:v:0 fast \
	\
	-ac 1 -c:a libfdk_aac -b:a 64k -ar 44100 \
	-ac:a:2 2 \
	\
	-y -f flv rtmp://192.168.2.120:1935/rpi2/movie
	#-maxrate:v:0 1100k -bufsize:v:0 8192k -crf:0 21 \
	# -maxrate:v:0 "${MAXRATE}k" -bufsize:v:0 8192k -crf:0 21 \
