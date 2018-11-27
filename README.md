## Description

This repository contains the official [Elasticsearch](https://www.elastic.co/products/elasticsearch) Docker image from [Elastic](https://www.elastic.co/).

Documentation can be found on the [Elastic web site](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

**Make sure you have read all the instructions properly, just "skimming through" will not help you.**

## Supported Docker versions

The images have been tested on Docker 18.06.1-ce.

## Requirements

A full build and test requires:

- Docker
- GNU Make
- Python 3.5 with Virtualenv

## Running a build
To build an image with a released version of Elasticsearch, check out the corresponding
branch for the version, and run Make while specifying the exact version desired.
Like this:
```
git checkout 6.3
ELASTIC_VERSION=6.3.1 make
```

To build an image with the latest snapshot of Elasticsearch, run:
```
make from-snapshot
make test-snapshot
```

## Contributing, issues and testing

Acceptance tests for the image are located in the test directory, and can be invoked with `make test`.

This image is built on [CentOS 7](https://github.com/CentOS/sig-cloud-instance-images/blob/CentOS-7/docker/Dockerfile).
