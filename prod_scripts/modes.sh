#!/bin/bash
if [ $# -ne 1 ]; then
        params=$(grep -E "^\s+\w+\)" $(readlink -f $0) | tr -d ")" )
        echo "Usage ./$0 <mode>"
        echo "Where mode is one of:"
        echo "$params"
        exit 1
fi

function comm {
        # echo $@
        echo "$@" | netcat -q0 localhost 9999
}
modes="$1"
case "$modes" in
        slides)
                comm set_video_a slides
                comm set_video_b cam1
                comm set_composite_mode side_by_side_preview
        ;;
        full)
                comm set_video_a cam1
                comm set_composite_mode fullscreen
        ;;
        start)
                comm set_composite_mode side_by_side_preview
                comm set_video_a slides
                comm set_video_b cam1
                comm set_audio_volume mic1 1
        ;;
        *)
                echo '? invalido'
        ;;
esac
