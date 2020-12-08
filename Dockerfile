FROM ubuntu:18.04 as django-container
WORKDIR /app/
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update && \
    apt-get -y install apache2 apache2-dev && \
    apt-get -y install gunicorn nginx && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y && \
    apt-get clean all

# Install system dependencies
RUN apt-get  update -y && \
    apt-get install -y \
    dumb-init \
    git \
    hostname \
    locales \
    openssl \
    sqlite3 \
    sudo \
    systemd \
    tar \
    curl \
    wget \
    netcat \
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
RUN . /app/bin/activate && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && pip3 install --upgrade pip && pip install mod_wsgi
RUN . /app/bin/activate && pip install django && django-admin.py startproject project . && pip uninstall django -y
RUN . /app/bin/activate && pip install django-prometheus && pip install croniter
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

# Set up nginx/gunicorn
ADD conf/gunicorn.service /etc/systemd/gunicorn.service
ADD conf/gunicorn.socket /etc/systemd/gunicorn.socket
ADD conf/nginx.conf /etc/nginx/nginx.conf

RUN mkdir /var/run/gunicorn && chown -R acait:acait /var/run/gunicorn && \
    mkdir /var/run/nginx && chown -R acait:acait /var/run/nginx && \
    mkdir /var/lib/nginx && chown -R acait:acait /var/lib/nginx && \
    chown -R acait:acait /var/log/nginx

# Set up apache2
ADD conf/apache2.conf /tmp/apache2.conf
ADD conf/envvars /tmp/envvars
RUN rm -rf /etc/apache2/sites-available/ && \
    mkdir /etc/apache2/sites-available/ && \
    rm -rf /etc/apache2/sites-enabled/ && \
    mkdir /etc/apache2/sites-enabled/ && \
    rm -rf /etc/apache2/conf-enabled/ && \
    mkdir /etc/apache2/conf-enabled/ && \
    rm /etc/apache2/apache2.conf && \
    cp /tmp/apache2.conf /etc/apache2/apache2.conf && \
    rm /etc/apache2/envvars &&\
    cp /tmp/envvars /etc/apache2/envvars &&\
    mkdir /etc/apache2/logs

RUN mkdir /var/lock/apache2 && mkdir /var/run/apache2
RUN chown -R acait:acait /var/lock/apache2 &&\
    chown -R acait:acait /var/run/apache2

USER acait

ENV PORT 8000
ENV DB sqlite3
ENV ENV localdev

CMD ["dumb-init", "--rewrite", "15:28", "/scripts/start.sh"]

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
