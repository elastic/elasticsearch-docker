SHELL=/bin/bash
ifndef ELASTICSEARCH_VERSION
ELASTICSEARCH_VERSION=5.0.0-alpha5
endif

export ELASTICSEARCH_VERSION

BASEIMAGE=container-registry.elastic.co/elasticsearch/elasticsearch-ci-base:latest
CONTAINERREGISTRY_IMAGE=container-registry.elastic.co/elasticsearch/elasticsearch:$(ELASTICSEARCH_VERSION)

# Common target to ensure BASEIMAGE is latest
pull-latest-baseimage:
	docker pull $(BASEIMAGE)

run-es-single: pull-latest-baseimage
	ES_NODE_COUNT=1 docker-compose up --build elasticsearch1

run-es-cluster: pull-latest-baseimage
	ES_NODE_COUNT=2 docker-compose up --build elasticsearch1 elasticsearch2

acceptance-test: single-node-test cluster-unicast-test

single-node-test: export ES_NODE_COUNT=1
single-node-test: pull-latest-baseimage
	docker-compose up -d --build elasticsearch1
	docker-compose up --build tester
	docker-compose stop
	docker-compose rm -f

cluster-unicast-test: export ES_NODE_COUNT=2
cluster-unicast-test: pull-latest-baseimage
	docker-compose up -d --build elasticsearch1 elasticsearch2
	docker-compose up --build tester
	docker-compose stop
	docker-compose rm -f

# Build docker image: "elasticsearch:$(ELASTICSEARCH_VERSION)"
build-es: acceptance-test

# Push $CONTAINERREGISTRY_IMAGE to container-registry.elastic.co/elasticsearch/ public repo
# Use the `infraelasticsearch` docker account for push
publish-elasticsearch-to-container-registry: build-es
	docker tag elasticsearch:$(ELASTICSEARCH_VERSION) $(CONTAINERREGISTRY_IMAGE)
	docker push $(CONTAINERREGISTRY_IMAGE)
