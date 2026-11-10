#!/bin/bash
set -eu
export XDG_SESSION_TYPE=wayland QT_QPA_PLATFORM=wayland
declare -p DBUS_SESSION_BUS_ADDRESS DISPLAY XDG_RUNTIME_DIR LANG LC_ALL XDG_MENU_PREFIX WAYLAND_DISPLAY QT_QPA_PLATFORM XDG_SESSION_TYPE > /tmp/brutall-session.env
dbus-update-activation-environment WAYLAND_DISPLAY XDG_SESSION_TYPE QT_QPA_PLATFORM
if [ -n "${LAB_OUTPUT_SCALE:-}" ]; then
    kscreen-doctor "output.X11-0.scale.$LAB_OUTPUT_SCALE" > /results/output-scale.log 2>&1
    sleep 0.5
fi
exec plasmashell --no-respawn
