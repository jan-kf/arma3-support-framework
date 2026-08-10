#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$XDG_RUNTIME_DIR" "$HOME/.local/share/Steam" "$HOME/.steam"
chmod 700 "$XDG_RUNTIME_DIR"

start_display() {
    local display_size="${PONTIFEX_DISPLAY_SIZE:-1280x720}"
    local display_width="${display_size%x*}"
    local display_height="${display_size#*x}"
    local weston_log="${PONTIFEX_LOG_DIR:-/tmp}/weston.log"
    local socket
    local vnc_dir="${PONTIFEX_LOG_DIR:-/tmp}/vnc"

    # Weston owns a virtual output only. It never opens a host DRM
    # device or becomes DRM master; its Xwayland module provides the private
    # X11 target required by Steam, DXVK, and Arma.
    export WAYLAND_DISPLAY="pontifex-wayland"
    unset DISPLAY XAUTHORITY
    # A kiosk shell keeps the game surface equal to the virtual output.  The
    # default desktop shell adds decorations, turning a 1280x720 request into
    # a smaller client surface and introducing focus-dependent window handling
    # that a headless test has no input device to resolve.
    local backend="headless"
    local backend_args=(--width="$display_width" --height="$display_height")
    if [[ "${PONTIFEX_COMPOSITOR_VNC:-0}" == "1" ]]; then
        # Weston's VNC backend captures the compositor output directly. This
        # avoids Xwayland framebuffer scraping, which cannot read DXVK's
        # redirected fullscreen surface. Docker publishes this port only on
        # the host loopback interface for manual diagnostics.
        backend="vnc"
        mkdir -p "$vnc_dir"
        chmod 700 "$vnc_dir"
        # This short-lived certificate is generated inside the confined
        # container solely for the loopback-published manual VNC endpoint.
        # It is neither host-trusted nor persisted with the Steam session.
        openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
            -keyout "$vnc_dir/key.pem" -out "$vnc_dir/cert.pem" \
            -subj "/CN=pontifex-manual-vnc" >/dev/null 2>&1
        chmod 600 "$vnc_dir/key.pem" "$vnc_dir/cert.pem"
        backend_args+=(--port=5900 --vnc-tls-cert="$vnc_dir/cert.pem" --vnc-tls-key="$vnc_dir/key.pem")
    fi
    weston --backend="$backend" --renderer="${PONTIFEX_COMPOSITOR_RENDERER:-gl}" --xwayland --shell=kiosk-shell.so \
        --socket="$WAYLAND_DISPLAY" \
        "${backend_args[@]}" \
        --no-config --log="$weston_log" >"${PONTIFEX_LOG_DIR:-/tmp}/weston.stdout.log" 2>&1 &
    export PONTIFEX_WESTON_PID=$!
    for _ in $(seq 1 100); do
        if [[ -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]]; then
            for socket in /tmp/.X11-unix/X*; do
                [[ -S "$socket" ]] || continue
                if xdpyinfo -display ":${socket##*X}" >/dev/null 2>&1; then
                    export DISPLAY=":${socket##*X}"
                    return 0
                fi
            done
        fi
        if ! kill -0 "$PONTIFEX_WESTON_PID" 2>/dev/null; then
            break
        fi
        sleep 0.1
    done
    echo "Weston headless Xwayland display did not start" >&2
    tail -100 "$weston_log" >&2 || true
    return 1
}

stop_display() {
    if [[ -n "${PONTIFEX_WESTON_PID:-}" ]] && kill -0 "$PONTIFEX_WESTON_PID" 2>/dev/null; then
        kill "$PONTIFEX_WESTON_PID" 2>/dev/null || true
        wait "$PONTIFEX_WESTON_PID" 2>/dev/null || true
    fi
}

start_network_state_bridge() {
    local bus_socket="$XDG_RUNTIME_DIR/system-bus"
    rm -f "$bus_socket"
    dbus-daemon --session --address="unix:path=${bus_socket}" --fork --nopidfile
    export DBUS_SYSTEM_BUS_ADDRESS="unix:path=${bus_socket}"
    /opt/pontifex/network-state-bridge.py >"${PONTIFEX_LOG_DIR:-/tmp}/network-state-bridge.log" 2>&1 &
    for _ in $(seq 1 50); do
        dbus-send --bus="$DBUS_SYSTEM_BUS_ADDRESS" --dest=org.freedesktop.NetworkManager \
            --type=method_call --print-reply /org/freedesktop/NetworkManager \
            org.freedesktop.DBus.Peer.Ping >/dev/null 2>&1 && return 0
        sleep 0.1
    done
    echo "private network-state bridge did not start" >&2
    return 1
}

case "${1:-status}" in
    preflight)
        start_display
        trap stop_display EXIT
        vulkaninfo --summary
        timeout 5s vkcube || [[ $? -eq 124 ]]
        ;;
    login)
        start_network_state_bridge
        start_display
        trap stop_display EXIT
        x11vnc -display "$DISPLAY" -forever -shared -nopw -listen 0.0.0.0 -rfbport 5900 >"${PONTIFEX_LOG_DIR:-/tmp}/x11vnc.log" 2>&1 &
        echo "Steam login display ready on container TCP 5900"
        dbus-run-session -- steam
        ;;
    test)
        shift
        # Match the interactive client desktop.  Arma's DirectX renderer is
        # unreliable on the historic 640x480 test surface.
        export PONTIFEX_DISPLAY_SIZE=1280x720
        start_network_state_bridge
        start_display
        trap stop_display EXIT
        if [[ "${PONTIFEX_TEST_VNC:-0}" == "1" ]]; then
            x11vnc -display "$DISPLAY" -forever -shared -nopw -listen 0.0.0.0 -rfbport 5900 >"${PONTIFEX_LOG_DIR:-/tmp}/x11vnc.log" 2>&1 &
        fi
        dbus-run-session -- /opt/pontifex/run-test.sh "$@"
        ;;
    manual)
        shift
        export PONTIFEX_DISPLAY_SIZE=1280x720
        start_network_state_bridge
        start_display
        trap stop_display EXIT
        dbus-run-session -- /opt/pontifex/run-test.sh "$@"
        ;;
    status)
        echo "Pontifex real-player client image"
        ;;
    *)
        exec "$@"
        ;;
esac
