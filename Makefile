SHELL=/bin/bash
export PATH := ./bin:./venv/bin:$(PATH)

ifndef ELASTIC_VERSION
ELASTIC_VERSION := $(shell cat version.txt)
endif

ifdef STAGING_BUILD_NUM
VERSION_TAG := $(ELASTIC_VERSION)-$(STAGING_BUILD_NUM)
else
VERSION_TAG := $(ELASTIC_VERSION)
endif

ELASTIC_REGISTRY := docker.elastic.co
VERSIONED_IMAGE := $(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:$(VERSION_TAG)

# When invoking docker-compose, use an extra config fragment to map Elasticsearch's
# listening port to the docker host.
DOCKER_COMPOSE := 'docker-compose -f docker-compose.yml -f docker-compose.hostports.yml'

.PHONY: test clean pristine run run-single run-cluster build push

# Default target, build *and* run tests
test: lint build docker-compose.yml
	./bin/testinfra tests

lint: venv
	flake8 tests

clean:
	docker-compose down -v
	docker-compose rm -f -v
	rm -f docker-compose.yml build/elasticsearch/Dockerfile

pristine: clean
	docker rmi -f $(VERSIONED_IMAGE)

run: run-single

run-single: build
	$(DOCKER_COMPOSE) up elasticsearch1

run-cluster: build
	$(DOCKER_COMPOSE) up elasticsearch1 elasticsearch2

# Build docker image: "elasticsearch:$(VERSION_TAG)"
build: clean dockerfile
	docker build -t $(VERSIONED_IMAGE) build/elasticsearch

push: test
	docker push $(VERSIONED_IMAGE)

# The tests are written in Python. Make a virtualenv to handle the dependencies.
venv: requirements.txt
	test -d venv || virtualenv --python=python3.5 venv
	pip install -r requirements.txt
	touch venv

# Generate the Dockerfile from a Jinja2 template.
dockerfile: venv templates/Dockerfile.j2
	jinja2 \
	  -D elastic_version='$(ELASTIC_VERSION)' \
	  -D version_tag='$(VERSION_TAG)' \
	  templates/Dockerfile.j2 > build/elasticsearch/Dockerfile

# Generate the docker-compose.yml from a Jinja2 template.
docker-compose.yml: venv templates/docker-compose.yml.j2
	jinja2 \
	  -D versioned_image='$(VERSIONED_IMAGE)' \
	  templates/docker-compose.yml.j2 > docker-compose.yml
