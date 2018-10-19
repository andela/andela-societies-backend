FROM python:3.6

MAINTAINER "Crispus Kamau <crispus.kamau@andela.com>"

LABEL application="andela-societies-backend"

# Prevent dpkg errors
ENV TERM=xterm-256color

# Set mirrors to Nearest Zone for faster builds
RUN sed -i "s/http:\/\/archive./http:\/\/nz.archive./g" /etc/apt/sources.list

# Install current stable versions of pip and wheel
RUN pip install pip==10.0.0 wheel==0.31.0

VOLUME /build

WORKDIR /application

COPY .git /application

COPY src /application

# Download requirements to the build cache
RUN pip download -d /build -r requirements.txt --no-input && \
  pip install -f /build -r requirements.txt

COPY scripts/test.sh /usr/local/bin/test.sh

RUN chmod +x /usr/local/bin/test.sh

ENTRYPOINT [ "test.sh" ]
