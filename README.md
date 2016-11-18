## Description

This is the official Elasticsearch image created by Elastic Inc.

Documentation can be found on the [Elastic web site](https://www.elastic.co/guide/en/elasticsearch/reference/master/docker.html).

## Supported Docker versions

The images have been tested on Docker 1.12.

## Contributing, issues and testing

This image is built on top of [elasticsearch-alpine-base](https://github.com/elastic/elasticsearch-alpine-base) and is based on [alpine:latest](https://hub.docker.com/_/alpine/).
The complete set of Elasticsearch tests is [regularly executed](https://elasticsearch-ci.elastic.co/view/Elasticsearch/job/elastic+elasticsearch+master+dockeralpine-periodic/) against it.

To report issues, please open an issue in [GitHub](https://github.com/elastic/elasticsearch-docker/issues).

To contribute, please fork and create a PR. Please ensure that tests pass by running `make`. Tests require [docker-compose](https://docs.docker.com/compose/install/).
