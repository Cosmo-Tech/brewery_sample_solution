FROM debian:trixie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ccache \
        clang-format \
        curl \
        default-jre \
        git \
        lsb-release \
        ninja-build \
        python3 \
        python3-dev \
        python3-venv \
        zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/ciuser

ARG uid=1000
ARG docker_gid=102
RUN groupadd -g "$uid" ciuser \
    && useradd -m -u "$uid" -g "$uid" ciuser \
    && groupadd -g "$docker_gid" -f docker \
    && gpasswd -a ciuser docker \
    && mkdir -p "$HOME/.cache" "$HOME/.ccache" \
    && chown -R ciuser:docker "$HOME"
USER ciuser:docker
WORKDIR $HOME

LABEL org.opencontainers.image.source=https://github.com/Cosmo-Tech/brewery_sample_solution
