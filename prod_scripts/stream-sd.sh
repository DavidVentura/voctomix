#!/bin/sh
ffmpeg -y -nostdin -hide_banner -loglevel warning -stats \
	-i tcp://localhost:15000 \
	-threads:0 0 \
	-aspect 16:9 \
	-c:v libx264 \
	-maxrate:v:0 1200k -bufsize:v:0 8192k -crf:0 21 \
	-pix_fmt:0 yuv420p -profile:v:0 high -g:v:0 50 \
	-preset:v:0 veryfast \
	\
	-ac 1 -c:a libfdk_aac -b:a 96k -ar 44100 \
	-ac:a:2 2 \
	\
	-y -f flv rtmp://192.168.2.120:1935/rpi2/movie
