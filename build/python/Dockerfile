FROM alpine:latest

RUN apk update && \
    apk upgrade && \
    apk add openssl python python-dev py2-pip && \
    rm -rf /var/cache/apk/*

RUN pip install --upgrade --quiet \
    requests \
    retrying \
    pytest

# Install test user
RUN adduser -D -u 1000 -h /home/testuser testuser

WORKDIR /home/testuser

USER testuser

RUN mkdir /home/testuser/tests
