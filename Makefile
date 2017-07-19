SHELL=/bin/bash
export PATH := ./bin:./venv/bin:$(PATH)

ifndef ELASTIC_VERSION
ELASTIC_VERSION := $(shell ./bin/elastic-version)
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
DOCKER_COMPOSE := docker-compose -f docker-compose.yml -f docker-compose.hostports.yml

.PHONY: all test lint clean pristine run run-single run-cluster build release-manager-snapshot push

# Default target, build *and* run tests
all: build test

test: lint build docker-compose.yml
	./bin/pytest tests
	./bin/pytest --single-node tests

lint: venv
	flake8 tests

clean:
	@if [ -f "docker-compose.yml" ]; then docker-compose down -v && docker-compose rm -f -v; fi
	rm -f docker-compose.yml build/elasticsearch/Dockerfile

pristine: clean
	docker rmi -f $(VERSIONED_IMAGE)

run: run-single

run-single: build docker-compose.yml
	$(DOCKER_COMPOSE) up elasticsearch1

run-cluster: build docker-compose.yml
	$(DOCKER_COMPOSE) up elasticsearch1 elasticsearch2

# Build docker image: "elasticsearch:$(VERSION_TAG)"
build: clean dockerfile
	docker build -t $(VERSIONED_IMAGE) build/elasticsearch

release-manager-snapshot: clean
	RELEASE_MANAGER=true ELASTIC_VERSION=$(ELASTIC_VERSION)-SNAPSHOT make dockerfile
	docker build --network=host -t $(VERSIONED_IMAGE)-SNAPSHOT build/elasticsearch

release-manager-release: clean
	RELEASE_MANAGER=true ELASTIC_VERSION=$(ELASTIC_VERSION) make dockerfile
	docker build --network=host -t $(VERSIONED_IMAGE) build/elasticsearch

# Push the image to the dedicated push endpoint at "push.docker.elastic.co"
push: test
	docker tag $(VERSIONED_IMAGE) push.$(VERSIONED_IMAGE)
	docker push push.$(VERSIONED_IMAGE)
	docker rmi push.$(VERSIONED_IMAGE)

# The tests are written in Python. Make a virtualenv to handle the dependencies.
venv: requirements.txt
	test -d venv || virtualenv --python=python3.5 venv
	pip install -r requirements.txt
	touch venv

# Generate the Dockerfile from a Jinja2 template.
dockerfile: venv templates/Dockerfile.j2
	jinja2 \
	  -D elastic_version='$(ELASTIC_VERSION)' \
	  -D staging_build_num='$(STAGING_BUILD_NUM)' \
	  -D release_manager='$(RELEASE_MANAGER)' \
	  -D base_xpack_path='$(BASE_XPACK_PATH)' \
	  templates/Dockerfile.j2 > build/elasticsearch/Dockerfile

# Generate the docker-compose.yml from a Jinja2 template.
docker-compose.yml: venv templates/docker-compose.yml.j2
	jinja2 \
	  -D version_tag='$(VERSION_TAG)' \
	  templates/docker-compose.yml.j2 > docker-compose.yml
