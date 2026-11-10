#!/bin/bash
set -eu
export XDG_RUNTIME_DIR=/tmp/brutall-runtime
export LANG=C.UTF-8 LC_ALL=C.UTF-8
export XDG_MENU_PREFIX=plasma-
mkdir -p "$XDG_RUNTIME_DIR" "$HOME/.config"
chmod 700 "$XDG_RUNTIME_DIR"
declare -p DBUS_SESSION_BUS_ADDRESS DISPLAY XDG_RUNTIME_DIR LANG LC_ALL XDG_MENU_PREFIX > /tmp/brutall-session.env
dbus-update-activation-environment DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE XDG_RUNTIME_DIR XDG_MENU_PREFIX
kbuildsycoca6 --noincremental > /results/kservice.log 2>&1
if [ "${LAB_SESSION:-x11}" = wayland ]; then
    mkdir -p "$HOME/bin"
    # Unprivileged copy: omit the distribution binary's scheduling capability,
    # which is unavailable in this container. No host capabilities are changed.
    cp /usr/bin/kwin_wayland "$HOME/bin/kwin_wayland"
    exec "$HOME/bin/kwin_wayland" --x11-display :99 --width "${LAB_WIDTH:-1920}" --height "${LAB_HEIGHT:-1080}" \
        --output-count "${LAB_OUTPUTS:-2}" --scale "${LAB_SCALE:-1}" --socket wayland-0 --no-lockscreen \
        --exit-with-session /project/lab/plasma/wayland-desktop.sh > /results/kwin-wayland.log 2>&1
fi
/usr/lib/x86_64-linux-gnu/libexec/kglobalacceld > /results/kglobalaccel.log 2>&1 &
for attempt in $(seq 1 30); do
    if /usr/lib/qt6/bin/qdbus org.kde.kglobalaccel /kglobalaccel >/dev/null 2>&1; then break; fi
    sleep 0.2
done
kwin_x11 --replace > /results/kwin.log 2>&1 &
plasmashell --no-respawn > /results/plasmashell.log 2>&1 &
wait
