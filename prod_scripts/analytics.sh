#!/bin/bash
function log {
    curl -s -i -XPOST 'http://graphs.eba:8086/write?db=curso' --data-binary "$1" >/dev/null &
}

function current_status {
    if [ ! -f /tmp/streaming_status ]; then
        exit 1
    fi
    status=$(</tmp/streaming_status)
    log "curso,type=streaming_status value=$status"
}

current_status
