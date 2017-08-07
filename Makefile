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
	ARTIFACTS_DIR=$(ARTIFACTS_DIR) ELASTIC_VERSION=$(ELASTIC_VERSION)-SNAPSHOT make dockerfile
	VERSIONED_IMAGE=$(VERSIONED_IMAGE)-SNAPSHOT make build-from-local-artifacts

release-manager-release: clean
	ARTIFACTS_DIR=$(ARTIFACTS_DIR) ELASTIC_VERSION=$(ELASTIC_VERSION) make dockerfile
	make build-from-local-artifacts

# Build from artifacts on the local filesystem, using an http server (running
# in a container) to provide the artifacts to the Dockerfile.
build-from-local-artifacts:
	docker run --rm -d --name=elasticsearch-docker-artifact-server \
	           --network=host -v $(ARTIFACTS_DIR):/mnt \
	           python:3 bash -c 'cd /mnt && python3 -m http.server'
	timeout 120 bash -c 'until curl -s localhost:8000 > /dev/null; do sleep 1; done'
	docker build --network=host -t $(VERSIONED_IMAGE) build/elasticsearch || \
	  (docker kill elasticsearch-docker-artifact-server; false)
	docker kill elasticsearch-docker-artifact-server

# Push the image to the dedicated push endpoint at "push.docker.elastic.co"
push: test
	docker tag $(VERSIONED_IMAGE) push.$(VERSIONED_IMAGE)
	docker push push.$(VERSIONED_IMAGE)
	docker rmi push.$(VERSIONED_IMAGE)

# The tests are written in Python. Make a virtualenv to handle the dependencies.
venv: requirements.txt
	@if [ -z $$PYTHON3 ]; then\
	    PY3_MINOR_VER=`python3 --version 2>&1 | cut -d " " -f 2 | cut -d "." -f 2`;\
	    if (( $$PY3_MINOR_VER < 5 )); then\
		echo "Couldn't find python3 in \$PATH that is >=3.5";\
		echo "Please install python3.5 or later or explicity define the python3 executable name with \$PYTHON3";\
	        echo "Exiting here";\
	        exit 1;\
	    else\
		export PYTHON3="python3.$$PY3_MINOR_VER";\
	    fi;\
	fi;\
	test -d venv || virtualenv --python=$$PYTHON3 venv;\
	pip install -r requirements.txt;\
	touch venv;\

# Generate the Dockerfile from a Jinja2 template.
dockerfile: venv templates/Dockerfile.j2
	jinja2 \
	  -D elastic_version='$(ELASTIC_VERSION)' \
	  -D staging_build_num='$(STAGING_BUILD_NUM)' \
	  -D artifacts_dir='$(ARTIFACTS_DIR)' \
	  -D base_xpack_path='$(BASE_XPACK_PATH)' \
	  templates/Dockerfile.j2 > build/elasticsearch/Dockerfile

# Generate the docker-compose.yml from a Jinja2 template.
docker-compose.yml: venv templates/docker-compose.yml.j2
	jinja2 \
	  -D version_tag='$(VERSION_TAG)' \
	  templates/docker-compose.yml.j2 > docker-compose.yml
