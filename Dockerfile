FROM ubuntu:18.04
WORKDIR /app/
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update && \
    apt-get -y install apache2 apache2-dev && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y && \
    apt-get clean all

# Install system dependencies
RUN apt-get  update -y&& \
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
ADD project/ /app/project
ADD scripts /scripts
ADD certs/ /app/certs
RUN mkdir /static


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
RUN groupadd -r acait -g 1000 && \
    useradd -u 1000 -rm -g acait -d /home/acait -s /bin/bash -c "container user" acait &&\
    chown -R acait:acait /app &&\
    chown -R acait:acait /static &&\
    chown -R acait:acait /home/acait &&\
    chown -R acait:acait /var/lock/apache2 &&\
    chown -R acait:acait /var/run/apache2  

RUN chmod -R +x /scripts


USER acait

ENV PORT 8000
ENV DB sqlite3
ENV ENV localdev

CMD [ "/scripts/start.sh" ]
