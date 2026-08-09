#!/usr/bin/env bash
set -euo pipefail

log_dir="${PONTIFEX_LOG_DIR:-/tmp}"
steam_root="$HOME/.steam/debian-installation"
game_dir="$steam_root/steamapps/common/Arma 3"

mkdir -p "$log_dir"
export PROTON_LOG=1
export PROTON_LOG_DIR="$log_dir"

copy_steam_diagnostics() {
    local diagnostics="$log_dir/steam-diagnostics"
    mkdir -p "$diagnostics/arma3-launcher"
    cp -a "$steam_root/logs/." "$diagnostics/" 2>/dev/null || true
    cp -a "$steam_root/steamapps/compatdata/107410/pfx/drive_c/users/steamuser/AppData/Local/Arma 3 Launcher/Logs/." \
        "$diagnostics/arma3-launcher/" 2>/dev/null || true
    ps -eww -o pid=,ppid=,etimes=,args= >"$diagnostics/processes.txt" 2>/dev/null || true
}
trap copy_steam_diagnostics EXIT

steam -silent >"$log_dir/steam.log" 2>&1 &
steam_pid=$!

steam_ready=0
for _ in $(seq 1 120); do
    # The runtime service appears before Steam's IPC endpoint.  The web helper
    # is only started after the authenticated Steam client is usable.
    if pgrep -u "$(id -u)" -f 'steamwebhelper' >/dev/null; then
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

if [[ ! -f "$game_dir/arma3_x64.exe" ]]; then
    echo "Installed Arma 3 player executable is missing" >&2
    exit 70
fi

# Steam owns the game-launch session and the Steamworks IPC endpoint.  Its Arma
# manifest starts arma3launcher.exe, which hands off to Arma3_x64.exe under
# Wine.  Wine does not expose the Windows executable name reliably to pgrep;
# keeping Steam alive lets the controller observe the actual in-game protocol
# rather than prematurely stopping a healthy player process.
echo "Launching Arma 3 through the authenticated Steam session" >&2
steam -silent -applaunch 107410 "$@"

while kill -0 "$steam_pid" 2>/dev/null; do
    sleep 5
done

echo "Steam exited while the real-player test was still running" >&2
exit 71
