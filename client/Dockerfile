FROM ubuntu:24.04

ARG CLIENT_UID=1000
ARG CLIENT_GID=1000
ARG NVIDIA_DRIVER_BRANCH=580

ENV DEBIAN_FRONTEND=noninteractive

RUN dpkg --add-architecture i386 \
    && sed -i 's/Components: main universe/Components: main universe restricted multiverse/' /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update \
    && printf 'steam steam/question select I AGREE\nsteam steam/license note\n' | debconf-set-selections \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        dbus-x11 \
        libegl1 \
        libegl1:i386 \
        libnvidia-gl-${NVIDIA_DRIVER_BRANCH}:i386 \
        libvulkan1 \
        libvulkan1:i386 \
        libx11-6 \
        libx11-6:i386 \
        libxcb1 \
        libxcb1:i386 \
        libxext6 \
        libxext6:i386 \
        iproute2 \
        procps \
        steam-installer \
        steam-devices \
        tini \
        vulkan-tools \
        x11vnc \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN existing_group="$(getent group "${CLIENT_GID}" | cut -d: -f1)" \
    && if [ -n "${existing_group}" ]; then groupmod --new-name pontifex "${existing_group}"; else groupadd --gid "${CLIENT_GID}" pontifex; fi \
    && existing_user="$(getent passwd "${CLIENT_UID}" | cut -d: -f1)" \
    && if [ -n "${existing_user}" ]; then usermod --login pontifex --home /home/pontifex --move-home --shell /bin/bash "${existing_user}"; else useradd --uid "${CLIENT_UID}" --gid "${CLIENT_GID}" --create-home --shell /bin/bash pontifex; fi

COPY container/entrypoint.sh /opt/pontifex/entrypoint.sh
COPY container/run-test.sh /opt/pontifex/run-test.sh
RUN chmod 0755 /opt/pontifex/entrypoint.sh /opt/pontifex/run-test.sh

USER pontifex
ENV HOME=/home/pontifex \
    DISPLAY=:99 \
    PATH=/usr/games:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    XDG_RUNTIME_DIR=/tmp/pontifex-xdg \
    NVIDIA_DRIVER_CAPABILITIES=graphics,display,utility,compat32

ENTRYPOINT ["/usr/bin/tini", "--", "/opt/pontifex/entrypoint.sh"]
CMD ["status"]
