FROM ubuntu:24.04 AS django-container
WORKDIR /app/
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Los_Angeles

# Install system dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get dist-upgrade -y && \
  apt-get clean && \
  apt-get install --no-install-recommends -y \
  build-essential \
  curl \
  dumb-init \
  git \
  hostname \
  libxml2-dev \
  libxmlsec1-dev \
  locales \
  netcat-openbsd \
  nginx \
  openssl \
  pkg-config \
  python3.12-dev \
  python3-venv \
  python3-pip \
  sqlite3 \
  sudo \
  supervisor \
  tar && \
  rm -rf /var/lib/apt/lists

RUN locale-gen en_US.UTF-8
# locale.getdefaultlocale() searches in this order
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8
ENV LANG=en_US.UTF-8

RUN python3 -m venv /app/

RUN /app/bin/pip install django && \
  /app/bin/django-admin startproject project . && \
  /app/bin/pip uninstall django -y

RUN /app/bin/pip install wheel gunicorn django-prometheus croniter tzdata

COPY project/ /app/project
COPY scripts /scripts
COPY certs/ /app/certs
RUN mkdir /static

# Override default ubuntu user with acait
RUN usermod -l acait -d /home/acait -m ubuntu && \
  groupmod -n acait ubuntu && \
  chown -R acait:acait /app /static /home/acait && \
  chmod -R +x /scripts

# Set up gunicorn/nginx
COPY conf/supervisord.conf /etc/supervisor/supervisord.conf
COPY conf/gunicorn.py /etc/gunicorn/conf.py
COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY conf/locations.conf /etc/nginx/includes/locations.conf

RUN mkdir /var/run/supervisor && chown -R acait:acait /var/run/supervisor && \
  mkdir /var/run/gunicorn && chown -R acait:acait /var/run/gunicorn && \
  mkdir /var/run/nginx && chown -R acait:acait /var/run/nginx && \
  chown -R acait:acait /var/lib/nginx /var/log/nginx && \
  chgrp acait /etc/nginx/nginx.conf && chmod g+w /etc/nginx/nginx.conf

# Append the uwca to the ca-bundle
RUN cat /app/certs/ca-uwca.crt >> /etc/ssl/certs/ca-certificates.crt

USER acait

ENV PYTHONPATH="${PYTHONPATH}:/app/project"
ENV PORT=8000
ENV DB=sqlite3
ENV ENV=localdev

CMD ["dumb-init", "--rewrite", "15:0", "/scripts/start.sh"]

FROM django-container AS django-test-container

# install test tooling
USER root
RUN apt-get update && \
    apt-get install --no-install-recommends -y nodejs npm unixodbc-dev && \
    rm -rf /var/lib/apt/lists

USER acait
RUN . /app/bin/activate && pip install --no-cache-dir \
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
