FROM ubuntu:18.04 as django-container
WORKDIR /app/
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y && \
    apt-get clean all && \
    apt-get install -y \
    dumb-init \
    git \
    hostname \
    locales \
    openssl \
    sqlite3 \
    sudo \
    tar \
    curl \
    wget \
    netcat \
    nginx \
    python-setuptools \
    build-essential\
    python3.6-dev \
    python3-venv \
    libxml2-dev \
    libxmlsec1-dev \
    python-pip

RUN locale-gen en_US.UTF-8
# locale.getdefaultlocale() searches in this order
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8

RUN python3 -m venv /app/
RUN . /app/bin/activate && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    pip3 install --upgrade pip
RUN . /app/bin/activate && \
    pip install django && \
    django-admin.py startproject project . && \
    pip uninstall django -y
RUN . /app/bin/activate && \
    pip install supervisor && \
    pip install gunicorn && \
    pip install django-prometheus && \
    pip install croniter
ADD project/ /app/project
ADD scripts /scripts
ADD certs/ /app/certs
RUN mkdir /static

RUN groupadd -r acait -g 1000 && \
    useradd -u 1000 -rm -g acait -d /home/acait -s /bin/bash -c "container user" acait &&\
    chown -R acait:acait /app &&\
    chown -R acait:acait /static &&\
    chown -R acait:acait /home/acait &&\
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

USER acait

ENV PORT 8000
ENV DB sqlite3
ENV ENV localdev

CMD ["dumb-init", "--rewrite", "15:0", "/scripts/start.sh"]

FROM django-container as django-test-container

# install test tooling
USER root
RUN apt-get install -y nodejs npm gcc-4.8 unixodbc-dev

USER acait
RUN . /app/bin/activate &&\
    pip install pycodestyle coverage nodeenv &&\
    nodeenv -p &&\
    npm install npm@latest &&\
    npm install jshint -g &&\
    npm install eslint -g &&\
    npm install stylelint -g &&\
    npm install tslib -g &&\
    npm install datejs -g &&\
    npm install jquery -g &&\
    npm install moment -g &&\
    npm install moment-timezone -g &&\
    npm install jsdom@15.2.1 -g &&\
    npm install mocha -g &&\
    npm install nyc -g &&\
    npm install sinon -g &&\
    npm install coveralls -g

ENV NODE_PATH=/app/lib/node_modules
