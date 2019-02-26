FROM ubuntu:18.04
WORKDIR /app/
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update && \
    apt-get -y install apache2 apache2-dev && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y && \
    apt-get clean all

# Install system dependencies
RUN apt-get  update -y && \
    apt-get install -y \
    git \
    hostname \
    openssl \
    sqlite3 \
    sudo \
    tar \
    curl \
    wget \
    python-setuptools \
    build-essential\
    python-dev \
    libxml2-dev \
    libxmlsec1-dev \
    python-pip \
    libmysqlclient-dev

RUN apt-get install -y libxmlsec1-dev
RUN pip install virtualenv
RUN virtualenv /app/
RUN . /app/bin/activate && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && pip install --upgrade pip && pip install mod_wsgi && pip install boto3 watchtower && pip install mysqlclient
RUN . /app/bin/activate && pip install django && django-admin.py startproject project . && pip uninstall django -y
RUN . /app/bin/activate && pip install pyscss pkgconfig
RUN apt-get install npm -y && npm install npm@latest -g && npm install -g less
ADD /project /app/project
ADD /certs /app/certs

