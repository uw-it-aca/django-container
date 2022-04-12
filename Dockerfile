FROM ubuntu:20.04 as django-container
WORKDIR /app/
ENV PYTHONUNBUFFERED 1
ENV TZ America/Los_Angeles

# Install system dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get dist-upgrade -y && \
  apt-get clean all && \
  apt-get install -y \
  build-essential \
  curl \
  dumb-init \
  git \
  hostname \
  libxml2-dev \
  libxmlsec1-dev \
  locales \
  netcat \
  nginx \
  openssl \
  pkg-config \
  python-setuptools \
  python3.8-dev \
  python3-venv \
  python3-pip \
  sqlite3 \
  sudo \
  supervisor \
  tar

RUN locale-gen en_US.UTF-8
# locale.getdefaultlocale() searches in this order
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8

RUN python3 -m venv /app/
RUN /app/bin/pip install wheel gunicorn django-prometheus croniter

ADD project/ /var/project
ADD scripts /scripts
ADD certs/ /app/certs
RUN mkdir /static

RUN groupadd -r acait -g 1000 && \
  useradd -u 1000 -rm -g acait -d /home/acait -s /bin/bash -c "container user" acait && \
  chown -R acait:acait /app && \
  chown -R acait:acait /static && \
  chown -R acait:acait /home/acait && \
  chmod -R +x /scripts

# Set up gunicorn/nginx
ADD conf/supervisord.conf /etc/supervisor/supervisord.conf
ADD conf/gunicorn.py /etc/gunicorn/conf.py
ADD conf/nginx.conf /etc/nginx/nginx.conf
ADD conf/locations.conf /etc/nginx/includes/locations.conf

RUN mkdir /var/run/supervisor && chown -R acait:acait /var/run/supervisor && \
  mkdir /var/run/gunicorn && chown -R acait:acait /var/run/gunicorn && \
  mkdir /var/run/nginx && chown -R acait:acait /var/run/nginx && \
  chown -R acait:acait /var/lib/nginx && \
  chown -R acait:acait /var/log/nginx && \
  chgrp acait /etc/nginx/nginx.conf && chmod g+w /etc/nginx/nginx.conf

# Append the uwca to the ca-bundle
RUN cat /app/certs/ca-uwca.crt >> /etc/ssl/certs/ca-certificates.crt

USER acait

ENV PORT 8000
ENV DB sqlite3
ENV ENV localdev

CMD ["dumb-init", "--rewrite", "15:0", "/scripts/start.sh"]

FROM django-container as django-test-container

# install test tooling
USER root
RUN apt-get install -y nodejs npm unixodbc-dev

USER acait
RUN . /app/bin/activate && pip install pycodestyle coverage nodeenv && \
  nodeenv -p && \
  npm install npm@latest && \
  npm install -g \
  coveralls \
  datejs \
  eslint \
  jquery \
  jsdom@15.2.1 \
  jshint \
  mocha \
  moment \
  moment-timezone \
  nyc \
  sinon \
  stylelint \
  tslib

ENV NODE_PATH=/app/lib/node_modules
