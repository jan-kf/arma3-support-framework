#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$XDG_RUNTIME_DIR" "$HOME/.local/share/Steam" "$HOME/.steam"
chmod 700 "$XDG_RUNTIME_DIR"

start_display() {
    Xvfb "$DISPLAY" -screen 0 640x480x24 -nolisten tcp -ac >"${PONTIFEX_LOG_DIR:-/tmp}/xvfb.log" 2>&1 &
    export PONTIFEX_XVFB_PID=$!
    for _ in $(seq 1 50); do
        [[ -S "/tmp/.X11-unix/X${DISPLAY#:}" ]] && return 0
        sleep 0.1
    done
    echo "virtual display did not start" >&2
    return 1
}

case "${1:-status}" in
    preflight)
        start_display
        vulkaninfo --summary
        timeout 5s vkcube || [[ $? -eq 124 ]]
        ;;
    login)
        start_display
        x11vnc -display "$DISPLAY" -forever -shared -nopw -listen 0.0.0.0 -rfbport 5900 >"${PONTIFEX_LOG_DIR:-/tmp}/x11vnc.log" 2>&1 &
        echo "Steam login display ready on container TCP 5900"
        exec dbus-run-session -- steam
        ;;
    test)
        shift
        start_display
        exec dbus-run-session -- /opt/pontifex/run-test.sh "$@"
        ;;
    status)
        echo "Pontifex real-player client image"
        ;;
    *)
        exec "$@"
        ;;
esac
