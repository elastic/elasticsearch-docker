SHELL=/bin/bash
export PATH := ./bin:./venv/bin:$(PATH)

ifndef ELASTIC_VERSION
ELASTIC_VERSION=5.3.0
endif

ifdef STAGING_BUILD_NUM
IMAGETAG=$(ELASTIC_VERSION)-${STAGING_BUILD_NUM}
ES_DOWNLOAD_URL=http://staging.elastic.co/$(IMAGETAG)/downloads/elasticsearch
ES_JAVA_OPTS:=ES_JAVA_OPTS="-Des.plugins.staging=${STAGING_BUILD_NUM}"
else
IMAGETAG=$(ELASTIC_VERSION)
ES_DOWNLOAD_URL=https://artifacts.elastic.co/downloads/elasticsearch
endif

ELASTIC_REGISTRY=docker.elastic.co
VERSIONED_IMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:$(IMAGETAG)
LATEST_IMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:latest

export ELASTIC_VERSION
export ES_DOWNLOAD_URL
export ES_JAVA_OPTS
export VERSIONED_IMAGE

.PHONY: test clean run run-single run-cluster build push

# Default target, build *and* run tests
test: build venv
	./bin/testinfra --verbose tests

# Clean up left over containers and volumes from earlier failed runs
clean:
	docker-compose down -v && docker-compose rm -f -v

run: run-single

run-single: build
	ES_NODE_COUNT=1 docker-compose -f docker-compose.yml -f docker-compose.hostports.yml \
          up elasticsearch1

run-cluster: build
	ES_NODE_COUNT=2 docker-compose -f docker-compose.yml -f docker-compose.hostports.yml \
          up elasticsearch1 elasticsearch2

# Build docker image: "elasticsearch:$(IMAGETAG)"
build: clean
	docker-compose build --pull

push: test
	docker push $(VERSIONED_IMAGE)

# The tests are written in Python. Make a virtualenv to handle the dependencies.
venv: requirements.txt
	test -d venv || virtualenv --python=python3.5 venv
	pip install -r requirements.txt
	touch venv
