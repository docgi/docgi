FROM python:3.8.0-alpine3.10

RUN mkdir -p /home/docgi && mkdir -p /var/log/uwsgi/ && touch /var/log/uwsgi/dogi.log
WORKDIR /home/docgi

RUN apk update && \
    apk add gcc \
            postgresql-dev \
            python3-dev \
            musl-dev \
            jpeg-dev \
            zlib-dev \
            linux-headers
COPY requirements/ /tmp
RUN pip install -r /tmp/dev.txt
COPY . .
