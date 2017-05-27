#!/bin/bash
source ./default-config.sh
#ffmpeg -i ../blanker.h264 -c:v rawvideo -pix_fmt:v yuv420p -c:v rawvideo -pix_fmt yuv420p -r 25 -f rawvideo blanker.raw 
ffmpeg -i background.png  -c:v rawvideo -pix_fmt:v yuv420p -c:v rawvideo -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -frames 1 -f rawvideo background.raw 
