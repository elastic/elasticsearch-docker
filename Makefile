SHELL=/bin/bash
ELASTIC_REGISTRY := docker.elastic.co

export PATH := ./bin:./venv/bin:$(PATH)

# Determine the version to build. Override by setting ELASTIC_VERSION env var.
ELASTIC_VERSION := $(shell ./bin/elastic-version)

ifdef STAGING_BUILD_NUM
  VERSION_TAG := $(ELASTIC_VERSION)-$(STAGING_BUILD_NUM)
else
  VERSION_TAG := $(ELASTIC_VERSION)
endif

# Build different images tagged as :version-<flavor>
IMAGE_FLAVORS ?= basic platinum

# Which image flavor will additionally receive the plain `:version` tag
DEFAULT_IMAGE_FLAVOR ?= basic

VERSIONED_IMAGE ?= $(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:$(VERSION_TAG)

# When invoking docker-compose, use an extra config fragment to map Elasticsearch's
# listening port to the docker host.
# For the x-pack security enabled image (platinum), use the fragment we utilize for tests.
ifeq ($(DEFAULT_IMAGE_FLAVOR),platinum)
  DOCKER_COMPOSE := docker-compose \
	-f docker-compose-$(DEFAULT_IMAGE_FLAVOR).yml \
	-f tests/docker-compose-$(DEFAULT_IMAGE_FLAVOR).yml
else
  DOCKER_COMPOSE := docker-compose \
	-f docker-compose-$(DEFAULT_IMAGE_FLAVOR).yml \
	-f docker-compose.hostports.yml
endif

.PHONY: all dockerfile docker-compose test test-build lint clean pristine run run-single run-cluster build release-manager release-manager-snapshot push

# Default target, build *and* run tests
all: build test

# Test specified versions without building
test: lint docker-compose
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	pyfiglet -w 160 -f puffy "test: $(FLAVOR) image"; \
	./bin/pytest --image-flavor=$(FLAVOR) tests; \
	./bin/pytest --image-flavor=$(FLAVOR) --single-node tests; \
	)

# Build and test
test-build: lint build docker-compose

lint: venv
	flake8 tests

clean:
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	if [[ -f "docker-compose-$(FLAVOR).yml" ]]; then \
	  docker-compose -f docker-compose-$(FLAVOR).yml down && docker-compose -f docker-compose-$(FLAVOR).yml rm -f -v; \
	fi; \
	rm -f docker-compose-$(FLAVOR).yml; \
	rm -f tests/docker-compose-$(FLAVOR).yml; \
	rm -f build/elasticsearch/Dockerfile-$(FLAVOR); \
	)

pristine: clean
	-$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	docker rmi -f $(VERSIONED_IMAGE)-$(FLAVOR); \
	)
	-docker rmi -f $(VERSIONED_IMAGE)

# Give us an easy way to start the DEFAULT_IMAGE_FLAVOR
run: run-single

run-single: build docker-compose
	$(DOCKER_COMPOSE) up elasticsearch1

run-cluster: build docker-compose
	$(DOCKER_COMPOSE) up elasticsearch1 elasticsearch2

# Build docker image: "elasticsearch:$(VERSION_TAG)-$(FLAVOR)"
build: clean dockerfile
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	pyfiglet -f puffy -w 160 "Building: $(ELASTIC_VERSION)-$(FLAVOR)"; \
	docker build -t $(VERSIONED_IMAGE)-$(FLAVOR) -f build/elasticsearch/Dockerfile-$(FLAVOR) build/elasticsearch; \
	)

release-manager-snapshot: clean
	ARTIFACTS_DIR=$(ARTIFACTS_DIR) ELASTIC_VERSION=$(ELASTIC_VERSION)-SNAPSHOT make build-from-local-artifacts

release-manager-release: clean
	ARTIFACTS_DIR=$(ARTIFACTS_DIR) ELASTIC_VERSION=$(ELASTIC_VERSION) make build-from-local-artifacts

# Build from artifacts on the local filesystem, using an http server (running
# in a container) to provide the artifacts to the Dockerfile.
build-from-local-artifacts: dockerfile
	docker run --rm -d --name=elasticsearch-docker-artifact-server \
	           --network=host -v $(ARTIFACTS_DIR):/mnt \
	           python:3 bash -c 'cd /mnt && python3 -m http.server'
	timeout 120 bash -c 'until curl -s localhost:8000 > /dev/null; do sleep 1; done'
	-$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	pyfiglet -f puffy -w 160 "Building: $(ELASTIC_VERSION)-$(FLAVOR)"; \
	docker build --network=host -t $(VERSIONED_IMAGE)-$(FLAVOR) -f build/elasticsearch/Dockerfile-$(FLAVOR) build/elasticsearch || \
	(docker kill elasticsearch-docker-artifact-server; false); \
	)
	docker kill elasticsearch-docker-artifact-server

# Push the images to the dedicated push endpoint at "push.docker.elastic.co"
push: test
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	docker tag $(VERSIONED_IMAGE)-$(FLAVOR) push.$(VERSIONED_IMAGE)-$(FLAVOR); \
	echo; echo "Pushing $(VERSIONED_IMAGE)-$(FLAVOR)"; echo; \
	docker push push.$(VERSIONED_IMAGE)-$(FLAVOR); \
	docker rmi push.$(VERSIONED_IMAGE)-$(FLAVOR);\
	)

# Also push a plain versioned image based on DEFAULT_IMAGE_FLAVOR
# e.g. elasticsearch-6.0.0 and elasticsearch-6.0.0-oss are the same.
	@if [[ "$(IMAGE_FLAVORS)" != *"$(DEFAULT_IMAGE_FLAVOR)"* ]]; then\
	  echo;\
	  echo "I can't tag and push $(VERSIONED_IMAGE)";\
	  echo "because you didn't build the \"$(DEFAULT_IMAGE_FLAVOR)\" image (check your \$$IMAGE_FLAVORS).";\
	  echo;\
	  echo "Failing here.";\
	  echo;\
	  exit 1;\
	fi
	docker tag $(VERSIONED_IMAGE)-$(DEFAULT_IMAGE_FLAVOR) push.$(VERSIONED_IMAGE)
	echo; echo "Pushing $(VERSIONED_IMAGE)"; echo; \
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

# Generate the Dockerfiles for each image flavor from a Jinja2 template.
dockerfile: venv templates/Dockerfile.j2
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	 jinja2 \
	   -D elastic_version='$(ELASTIC_VERSION)' \
	   -D staging_build_num='$(STAGING_BUILD_NUM)' \
	   -D artifacts_dir='$(ARTIFACTS_DIR)' \
	   -D image_flavor='$(FLAVOR)' \
	   templates/Dockerfile.j2 > build/elasticsearch/Dockerfile-$(FLAVOR); \
	)

# Generate docker-compose and tests/docker-compose fragment files
# for each image flavor from a Jinja2 template.
docker-compose: venv templates/docker-compose.yml.j2 templates/docker-compose-fragment.yml.j2
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	 jinja2 \
	  -D version_tag='$(VERSION_TAG)-$(FLAVOR)' \
	  templates/docker-compose.yml.j2 > docker-compose-$(FLAVOR).yml; \
	 jinja2 \
	  -D image_flavor='$(FLAVOR)' \
	  templates/docker-compose-fragment.yml.j2 > tests/docker-compose-$(FLAVOR).yml; \
	)
