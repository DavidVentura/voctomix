#!/bin/bash
#ffmpeg -i ../blanker.h264 -c:v rawvideo -pix_fmt:v yuv420p -c:v rawvideo -pix_fmt yuv420p -r 25 -f rawvideo blanker.raw 
#ffmpeg -i background.png  -c:v rawvideo -pix_fmt:v yuv420p -c:v rawvideo -pix_fmt yuv420p -frames 1 -f rawvideo background.raw 
