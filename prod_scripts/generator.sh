#!/bin/bash
source ./default-config.sh
#ffmpeg -i ../blanker.h264 -c:v rawvideo -pix_fmt:v yuv420p -c:v rawvideo -pix_fmt yuv420p -r 25 -f rawvideo blanker.raw 
if [ $# -ne 1 ]; then
    echo "usage $0 filename"
    exit 1
fi
if [ ! -f "$1" ]; then
    echo "$1 not a file"
    exit 1
fi
ffmpeg -i "$1" -c:v rawvideo -pix_fmt:v yuv420p -c:v rawvideo -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -frames 1 -f rawvideo background.raw 
