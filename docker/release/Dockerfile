FROM python:3.6

MAINTAINER "Crispus Kamau <crispus.kamau@andela.com>"

LABEL application="andela-societies-backend"

# Prevent dpkg errors
ENV TERM=xterm-256color

# Set mirrors to Nearest Zone for faster builds
RUN sed -i "s/http:\/\/archive./http:\/\/nz.archive./g" /etc/apt/sources.list

# Install current stable version of pip
RUN pip install pip==10.0.0

WORKDIR /application

COPY src/requirements.txt /application/requirements.txt

RUN pip install -r requirements.txt

COPY src /application
