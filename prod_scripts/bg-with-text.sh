#!/bin/bash

set -eu
if [ $# -ne 1 ]; then
    echo "Usage: $0 class name"
    exit 1
fi

FONT1="Museo Sans"
FONT2="Museo Sans Cyrl 100"
BLACK="4278190080"

TITLE="Estás viendo:"
CLASS="$1"

length=${#CLASS}
MAXLENGTH=48
if [ $length -gt $MAXLENGTH ]; then
    echo "Max length for classname is $MAXLENGTH, your input has $length chars"
    exit 1
fi

gst-launch-1.0 -q filesrc location='../str.png' ! pngdec ! videoconvert ! video/x-raw,format=I420 ! imagefreeze ! video/x-raw,framerate=25/1 !\
    textoverlay text="<span size='11000'>$CLASS</span>"\
    valignment=absolute halignment=4 y-absolute=0.91 x-absolute=0 deltax=15 font-desc="$FONT1" draw-shadow=false draw-outline=false color="$BLACK" !\
    textoverlay text="<span size='11000'>$TITLE</span>"\
    valignment=absolute halignment=4 y-absolute=0.85 x-absolute=0 deltax=15 font-desc="$FONT2" draw-shadow=false draw-outline=false color="$BLACK" !\
    queue ! matroskamux ! tcpclientsink blocksize=16384 host=localhost port=16000
