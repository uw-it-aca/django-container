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
    locales \
    openssl \
    sqlite3 \
    sudo \
    tar \
    curl \
    wget \
    python-setuptools \
    build-essential\
    python3.6-dev \
    python3-venv \
    libxml2-dev \
    libxmlsec1-dev \
    python-pip \
    libmysqlclient-dev

RUN locale-gen en_US.UTF-8
# locale.getdefaultlocale() searches in this order
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8

RUN python3 -m venv /app/
RUN . /app/bin/activate && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && pip3 install --upgrade pip && \
    pip install mod_wsgi boto3 watchtower mysqlclient dj-database-url
RUN . /app/bin/activate && pip install django && django-admin.py startproject project . && pip uninstall django -y
ADD project/ /app/project
