# syntax=docker/dockerfile:1
FROM debian:13-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=secret,id=ca_bundle,required=true \
    apt-get -o Acquire::https::CaInfo=/run/secrets/ca_bundle update && \
    apt-get -o Acquire::https::CaInfo=/run/secrets/ca_bundle install -y --no-install-recommends \
      plasma-desktop plasma-workspace kwin-x11 kwin-wayland kwin-addons \
      breeze breeze-icon-theme kde-style-breeze kde-config-gtk-style \
      dolphin kate konsole systemsettings qdbus-qt6 \
      plasma-nm plasma-pa powerdevil \
      xvfb x11-xserver-utils x11-utils xdotool dbus-x11 procps \
      python3 python3-pyside6.qtgui python3-pyside6.qtqml python3-pyside6.qtquick \
      python3-pyside6.qttest python3-pyside6.qtnetwork python3-pil \
      qml6-module-qtquick-controls qml6-module-qtquick-layouts \
      qml6-module-qtquick-templates qml6-module-qtquick-window qml6-module-qtqml-workerscript \
      libgl1-mesa-dri fonts-dejavu-core libglib2.0-bin && \
    rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 1000 --shell /bin/bash tester
USER tester
WORKDIR /project
ENV DISPLAY=:99 QT_QUICK_BACKEND=software LIBGL_ALWAYS_SOFTWARE=1 \
    QT_X11_NO_MITSHM=1 XDG_CURRENT_DESKTOP=KDE XDG_SESSION_DESKTOP=KDE \
    XDG_SESSION_TYPE=x11 KDE_FULL_SESSION=true WELCOME_PYTHON=/usr/bin/python3
CMD ["bash"]
