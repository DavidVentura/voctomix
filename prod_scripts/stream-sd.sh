#!/bin/sh
ffmpeg -y -nostdin \
	-i tcp://localhost:11000 \
	-threads:0 0 \
	-aspect 16:9 \
	-c:v libx264 \
	-maxrate:v:0 1100k -bufsize:v:0 8192k -crf:0 20 \
	-pix_fmt:0 yuv420p -profile:v:0 high -g:v:0 50 \
	-preset:v:0 superfast \
	\
	-ac 1 -c:a libfdk_aac -b:a 96k -ar 44100 \
	-ac:a:2 2 \
	\
	-y -f flv rtmp://192.168.2.120:1935/rpi2/movie

#-preset:v:0 veryfast \
