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
        sleep 0.01
}
function log {
    curl -s -i -XPOST 'http://graphs.eba:8086/write?db=curso' --data-binary "$1" >/dev/null &
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
                comm set_audio_volume mic1 1
        ;;
        start)
                comm set_composite_mode side_by_side_preview
                comm set_video_a slides
                comm set_video_b cam1
                comm set_audio_volume mic1 1
                comm set_audio_volume slides 0.2
                comm set_stream_live
                log "curso,type=streaming_status value=1"
                echo '1' >/tmp/streaming_status
        ;;
        blank)
                comm set_stream_blank nostream
                log "curso,type=streaming_status value=0"
                echo '0' >/tmp/streaming_status
        ;;
        live)
                comm set_stream_live
                log "curso,type=streaming_status value=1"
                echo '1' >/tmp/streaming_status
        ;;
        *)
                echo '? invalido'
        ;;
esac
