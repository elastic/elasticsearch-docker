SHELL=/bin/bash
ifndef ELASTIC_VERSION
ELASTIC_VERSION=5.0.0-rc1
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
BASEIMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch-alpine-base:latest
VERSIONED_IMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:$(IMAGETAG)
LATEST_IMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:latest

export ELASTIC_VERSION
export ES_DOWNLOAD_URL
export ES_JAVA_OPTS
export VERSIONED_IMAGE

.PHONY: build clean cluster-unicast-test pull-latest-baseimage push run-es-cluster run-es-single single-node-test test

# Default target, build *and* run tests
test: single-node-test cluster-unicast-test

# Common target to ensure BASEIMAGE is latest
pull-latest-baseimage:
	docker pull $(BASEIMAGE)

# Clean up left over containers and volumes from earlier failed runs
clean:
	docker-compose down -v && docker-compose rm -f -v

run-es-single: pull-latest-baseimage
	ES_NODE_COUNT=1 docker-compose -f docker-compose.yml -f docker-compose.hostports.yml up --build elasticsearch1

run-es-cluster: pull-latest-baseimage
	ES_NODE_COUNT=2 docker-compose -f docker-compose.yml -f docker-compose.hostports.yml up --build elasticsearch1 elasticsearch2

single-node-test: export ES_NODE_COUNT=1
single-node-test: pull-latest-baseimage clean
	docker-compose up -d --build elasticsearch1
	docker-compose build tester
	docker-compose run tester
	docker-compose down -v

cluster-unicast-test: export ES_NODE_COUNT=2
cluster-unicast-test: pull-latest-baseimage clean
	docker-compose up -d --build elasticsearch1 elasticsearch2
	docker-compose build tester
	docker-compose run tester
	docker-compose down -v

# Build docker image: "elasticsearch:$(IMAGETAG)"
build: pull-latest-baseimage clean
	docker-compose build --pull elasticsearch1

# Push to registry. Only push latest if not a staging build.
push: test
	docker push $(VERSIONED_IMAGE)

	if [ -z $$STAGING_BUILD_NUM ]; then \
		docker push $(LATEST_IMAGE); \
	fi
