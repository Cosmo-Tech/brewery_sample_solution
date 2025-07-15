FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ccache \
        clang-format \
        curl \
        git \
        ninja-build \
        python3 \
        python3-venv \
        python3-dev \
        zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG JDK_NAME=temurin-11-jdk
RUN curl -sSL https://packages.adoptium.net/artifactory/api/gpg/key/public > /etc/apt/trusted.gpg.d/adoptium.asc \
  && echo "deb [signed-by=/etc/apt/trusted.gpg.d/adoptium.asc] https://packages.adoptium.net/artifactory/deb bookworm main" > /etc/apt/sources.list.d/adoptium.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends ${JDK_NAME} \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/ciuser \
    JAVA_HOME=/usr/lib/jvm/${JDK_NAME}-amd64

ARG uid=1000
ARG docker_gid=102
RUN groupadd -g $uid ciuser \
    && useradd -m -u $uid -g $uid ciuser \
    && groupadd -g $docker_gid -f docker \
    && gpasswd -a ciuser docker \
    && mkdir -p $HOME/.cache $HOME/.ccache $HOME/.embedpostgresql $HOME/.gradle $HOME/.m2 \
    && chown -R ciuser:docker $HOME
USER ciuser:docker
WORKDIR $HOME

LABEL org.opencontainers.image.source=https://github.com/Cosmo-Tech/brewery_sample_solution

CMD bash
