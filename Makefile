SHELL=/bin/bash
ifndef ELASTICSEARCH_VERSION
ELASTICSEARCH_VERSION=5.0.0-rc1
endif

ifdef STAGING_BUILD_NUM
IMAGETAG=$(ELASTICSEARCH_VERSION)-${STAGING_BUILD_NUM}
ES_DOWNLOAD_URL=http://staging.elastic.co/$(IMAGETAG)/downloads/elasticsearch
ES_JAVA_OPTS:=ES_JAVA_OPTS="-Des.plugins.staging=${STAGING_BUILD_NUM}"
else
IMAGETAG=$(ELASTICSEARCH_VERSION)
ES_DOWNLOAD_URL=https://artifacts.elastic.co/downloads/elasticsearch
endif

export ELASTICSEARCH_VERSION
export ES_DOWNLOAD_URL
export ES_JAVA_OPTS
export IMAGETAG

ELASTIC_REGISTRY=docker.elastic.co
BASEIMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch-alpine-base:latest
ELASTICREGISTRY_ESIMAGE=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:$(IMAGETAG)
ELASTICREGISTRY_ESIMAGE_LATESTTAG=$(ELASTIC_REGISTRY)/elasticsearch/elasticsearch:latest

.PHONY: acceptance-test build clean-up-from-last-runs cluster-unicast-test push pull-latest-baseimage run-es-cluster run-es-single single-node-test

# Common target to ensure BASEIMAGE is latest
pull-latest-baseimage:
	docker pull $(BASEIMAGE)

# Clean up left over containers and volumes from earlier failed runs
clean-up-from-last-runs:
	docker-compose down -v && docker-compose rm -f -v
	rm -rf tests/__pycache__
	rm -f tests/*.pyc

run-es-single: pull-latest-baseimage
	ES_NODE_COUNT=1 docker-compose up --build elasticsearch1

run-es-cluster: pull-latest-baseimage
	ES_NODE_COUNT=2 docker-compose up --build elasticsearch1 elasticsearch2

acceptance-test: single-node-test cluster-unicast-test

single-node-test: export ES_NODE_COUNT=1
single-node-test: pull-latest-baseimage clean-up-from-last-runs
	docker-compose up -d --build elasticsearch1
	docker-compose build tester
	docker-compose run tester
	docker-compose down -v

cluster-unicast-test: export ES_NODE_COUNT=2
cluster-unicast-test: pull-latest-baseimage clean-up-from-last-runs
	docker-compose up -d --build elasticsearch1 elasticsearch2
	docker-compose build tester
	docker-compose run tester
	docker-compose down -v

# Build docker image: "elasticsearch:$(IMAGETAG)"
build: acceptance-test

# Push $ELASTICREGISTRY_ESIMAGE to docker.elastic.co/elasticsearch/ public repo
# Also tag elasticsearch:latest to this image (master branch always contains latest)
push: build
	docker tag elasticsearch:$(IMAGETAG) $(ELASTICREGISTRY_ESIMAGE)
	docker push $(ELASTICREGISTRY_ESIMAGE)

	# Only push latest if not a staging build
	if [ -z $$STAGING_BUILD_NUM ]; then \
		docker tag elasticsearch:$(IMAGETAG) $(ELASTICREGISTRY_ESIMAGE_LATESTTAG); \
		docker push $(ELASTICREGISTRY_ESIMAGE_LATESTTAG); \
	fi
