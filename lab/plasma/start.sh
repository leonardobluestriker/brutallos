#!/bin/bash
set -eu
mkdir -p /results
if [ -f /tmp/.X99-lock ] && ! xdpyinfo >/dev/null 2>&1; then
    # Only this disposable container owns :99; clean stale files after restart.
    rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
fi
Xvfb :99 -screen 0 "${LAB_RESOLUTION:-1920x1080x24}" -nolisten tcp -noreset -ac > /results/xvfb.log 2>&1 &
for attempt in $(seq 1 60); do
    if xdpyinfo >/dev/null 2>&1; then break; fi
    sleep 0.25
done
exec dbus-run-session -- bash /project/lab/plasma/session.sh
