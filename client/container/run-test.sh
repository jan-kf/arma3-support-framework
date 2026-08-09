#!/usr/bin/env bash
set -euo pipefail

steam -silent >"${PONTIFEX_LOG_DIR:-/tmp}/steam.log" 2>&1 &
steam_pid=$!

steam_ready=0
for _ in $(seq 1 120); do
    if pgrep -u "$(id -u)" -f 'steamwebhelper|steam-runtime' >/dev/null; then
        steam_ready=1
        break
    fi
    if ! kill -0 "$steam_pid" 2>/dev/null; then
        echo "Steam exited before becoming ready" >&2
        wait "$steam_pid"
    fi
    sleep 1
done
if [[ "$steam_ready" -ne 1 ]]; then
    echo "Steam did not become ready" >&2
    exit 69
fi

steam -silent -applaunch 107410 "$@"

started=0
for _ in $(seq 1 120); do
    if pgrep -u "$(id -u)" -f 'arma3_x64.exe' >/dev/null; then
        started=1
        break
    fi
    sleep 1
done
if [[ "$started" -ne 1 ]]; then
    echo "Arma 3 player executable did not start" >&2
    exit 70
fi

while pgrep -u "$(id -u)" -f 'arma3_x64.exe' >/dev/null; do
    sleep 1
done
