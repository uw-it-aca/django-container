# syntax=docker/dockerfile:1
# Multi-stage Dockerfile using Ubuntu Chisel for minimal image size
# Based on existing Dockerfile but with chisel optimization

ARG UBUNTU_RELEASE=24.04 CHISEL_VERSION=v1.5.0

# Stage 1: Extract minimal Ubuntu/Python runtime with Chisel
FROM ubuntu:$UBUNTU_RELEASE AS chisel-base
ARG UBUNTU_RELEASE CHISEL_VERSION

# Install system dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get dist-upgrade -y && \
  apt-get clean && \
  apt-get install --no-install-recommends -y \
  locales \
  build-essential \
  pkg-config \
  python3.12-dev \
  python3-pip \
  python3-venv \
  libpq-dev \
  curl \
  git \
  sudo \
  tar && \
  rm -rf /var/lib/apt/lists/*

# Add custom chisel slice definitions
RUN git clone -b ubuntu-${UBUNTU_RELEASE} https://github.com/canonical/chisel-releases ./custom-release
COPY ./slices ./custom-release/slices/

# Install chisel tool
RUN curl -S --location https://github.com/canonical/chisel/releases/download/${CHISEL_VERSION}/chisel_${CHISEL_VERSION}_linux_amd64.tar.gz \
    | tar --extract --gunzip --directory=/usr/local/bin chisel

# Use chisel cut to extract only essential packages needed for Python/Django runtime
RUN mkdir /rootfs && \
   chisel cut --release ./custom-release --root /rootfs \
    base-files_base \
    passwd_config \
    ca-certificates_data \
    bash_bins \
    dash_bins \
    coreutils_chmod \
    coreutils_chown \
    coreutils_delaying \
    coreutils_rm-utility \
    coreutils_test \
    libpsl5t64_libs \
    libssl3t64_libcrypto \
    libssl3t64_libs \
    openssl_config \
    openssl_data \
    python3.12-venv_ensurepip \
    python3-minimal_bins \
    libc6_libs \
    libpq5_libs \
    libxml2_libs \
    libxmlsec1t64_libs \
    libxmlsec1t64-openssl_libs \
    git_bins \
    git_http-support \
    netcat-openbsd_bins \
    dumb-init_bins \
    supervisor_bins \
    hostname_bins \
    sqlite3_bins \
    nginx_bins

# set locale on /rootfs
RUN /usr/sbin/locale-gen en_US.UTF-8
RUN mkdir -p /rootfs/usr/lib/locale && \
    cp /usr/lib/locale/locale-archive /rootfs/usr/lib/locale/locale-archive

# install python3 virtual env, django startproject and
# common python packages (and those req'ing gcc) then
# copy to /rootfs/app to preserve paths in venv
RUN mkdir -p /app && \
    /usr/bin/python3 -m venv /app && \
    /app/bin/pip install django && \
    /app/bin/django-admin startproject project /app && \
    /app/bin/pip uninstall django -y && \
    /app/bin/pip install wheel \
        gunicorn \
        django-prometheus \
        croniter \
        tzdata \
        psycopg[c] && \
    mv /app /rootfs

COPY project/ /rootfs/app/project
COPY scripts /rootfs/scripts
COPY certs/ /rootfs/app/certs
RUN mkdir /rootfs/static

# Override default ubuntu user with acait and set ownership
RUN usermod -l acait -d /home/acait -m ubuntu && \
    groupmod -n acait ubuntu && \
    mkdir -p /rootfs/etc && \
    grep "^acait:" /etc/passwd >> /rootfs/etc/passwd && \
    grep "^acait:" /etc/group >> /rootfs/etc/group && \
    mv /home/acait /rootfs/home/acait && \
    chown -R acait:acait /rootfs/app /rootfs/static /rootfs/home/acait && \
    chmod -R +x /rootfs/scripts

# Set up gunicorn/nginx
COPY conf/supervisord.conf /rootfs/etc/supervisor/supervisord.conf
COPY conf/gunicorn.py /rootfs/etc/gunicorn/conf.py
COPY conf/nginx.conf /rootfs/etc/nginx/nginx.conf
COPY conf/locations.conf /rootfs/etc/nginx/includes/locations.conf

RUN mkdir /rootfs/var/run/supervisor && chown -R acait:acait /rootfs/var/run/supervisor && \
  mkdir /rootfs/var/run/gunicorn && chown -R acait:acait /rootfs/var/run/gunicorn && \
  mkdir /rootfs/var/run/nginx && chown -R acait:acait /rootfs/var/run/nginx && \
  chown -R acait:acait /rootfs/var/lib/nginx /rootfs/var/log/nginx && \
  chgrp acait /rootfs/etc/nginx/nginx.conf && chmod g+w /rootfs/etc/nginx/nginx.conf

# Append the uwca to the ca-bundle
RUN cat /rootfs/app/certs/ca-uwca.crt >> /rootfs/etc/ssl/certs/ca-certificates.crt

# Stage 2: Base Django application image (FROM scratch with chisel base)
FROM scratch AS base-django-container

# Copy minimal Ubuntu/Python runtime from chisel extraction
COPY --from=chisel-base /rootfs /

# Stage 3: Django application image (from chiseled base container)
FROM base-django-container AS django-container

WORKDIR /app/

ENV PATH="/usr/bin:/app/bin:\$PATH" \
    PYTHONUNBUFFERED=1 \
    TZ=America/Los_Angeles

# locale.getdefaultlocale() searches in this order
ENV LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LANG=en_US.UTF-8

# Health check to verify application responsiveness
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /app/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000')" || exit 1

USER acait

ENV PORT=8000
ENV DB=sqlite3
ENV ENV=localdev

CMD ["dumb-init", "--rewrite", "15:0", "/scripts/start.sh"]

# Stage 4: Test container for CI/development (includes test tooling)
FROM ubuntu:24.04 AS django-test-container

ARG DEBIAN_FRONTEND=noninteractive

# Copy Django app and runtime from chiseled django-container
COPY --from=django-container /app /app
COPY --from=django-container /scripts /scripts
COPY --from=django-container /etc/supervisor /etc/supervisor
COPY --from=django-container /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=django-container /etc/nginx /etc/nginx
COPY --from=django-container /home/acait /home/acait
COPY --from=django-container /etc/passwd /etc/passwd
COPY --from=django-container /etc/group /etc/group

WORKDIR /app/

# Install system dependencies for testing BEFORE modifying PATH
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    ca-certificates \
    libatomic1 \
    nodejs \
    npm \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Now set custom PATH after apt-get is no longer needed
ENV PATH="/app/bin:/usr/bin:\$PATH" \
    PYTHONUNBUFFERED=1 \
    TZ=America/Los_Angeles \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LANG=en_US.UTF-8

# Fix ownership of copied files so acait user can access them
RUN chown -R acait:acait /app /scripts /home/acait

USER acait
RUN . /app/bin/activate && /app/bin/python -m pip install --no-cache-dir \
  pycodestyle \
  coverage \
  nodeenv && \
  nodeenv -p && \
  npm install npm@latest && \
  npm install -g \
  coveralls \
  datejs \
  eslint \
  jquery \
  jsdom \
  jshint \
  mocha \
  moment \
  moment-timezone \
  nyc \
  sinon \
  stylelint \
  tslib

ENV NODE_PATH=/app/lib/node_modules

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /app/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000')" || exit 1

CMD ["dumb-init", "--rewrite", "15:0", "/scripts/start.sh"]
