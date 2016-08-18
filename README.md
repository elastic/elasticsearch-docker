## Description

This is the official Elasticsearch image created by Elastic Inc.

## Image tags and hosting

The image is hosted in Elastic's own docker registry: `container-registry.elastic.co/elasticsearch`

Available tags:

- 5.0.0-alpha5
- latest -> 5.0.0-alpha5

## Using the image

To save some keystrokes first set:

``` shell
export ELASTIC_REG=container-registry.elastic.co/elasticsearch

```

### Single node example

Example:

`docker run -d -v esdatavolume:/usr/share/elasticsearch/data $ELASTIC_REG/elasticsearch:5.0.0-alpha5`

This example uses a [Docker named volume](https://docs.docker.com/engine/tutorials/dockervolumes/) called `esdatavolume` which will be created if not present.

### Cluster example

*WARNING: You need to explicitly set [discovery.zen.minimum_master_nodes](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery-zen.html)*


`docker run -d -P -v esdatavolume1:/usr/share/elasticsearch/data --name elasticsearch1 $ELASTIC_REG/elasticsearch:5.0.0-alpha5 bin/elasticsearch -E discovery.zen.minimum_master_nodes=2`

`docker run -d -P -v esdatavolume2:/usr/share/elasticsearch/data --name elasticsearch2 --link elasticsearch1 $ELASTIC_REG/elasticsearch:5.0.0-alpha5 bin/elasticsearch -E discovery.zen.minimum_master_nodes=2 -E discovery.zen.ping.unicast.hosts=elasticsearch1`

### Logging

Elasticsearch logs go to the console.

### Notes for production use and defaults

1. It is important to correctly set capabilities and ulimits via Docker cli. The following are required, also see docker-compose.yml:
   `--cap-add=IPC_LOCK --ulimit memlock=-1:-1 --ulimit nofile=65536:65536`

2. Define [discovery.zen.minimum_master_nodes](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery-zen.html) based on your requirements

3. By default the image will use 2g for Java Heap. You need to define the env var `ES_JAVA_OPTS` to match your requirements, e.g. to use 16GB use -e ES_JAVA_OPTS="-Xms16g -Xms=16g" with `docker run`. It is also recommended to set a memory limit for the container.

4. It is recommended to pin your deployments to a specific version of the Elasticsearch Docker image, especially if you are using an orchestration framework like Kubernetes, Amazon ECS or Docker Swarm.

5. Always use a volume bound on `/usr/share/elasticsearch/data`, as seen above, for the following reasons:

  - The data of your elasticsearch node won't be lost if the container gets killed
  - Elasticsearch is IO sensitive and you should not be using the Docker Storage Driver
  - Allows the use of advanced [Docker volume plugins](https://docs.docker.com/engine/extend/plugins/#volume-plugins)

6. Consider centralizing your logs by using a different [logging driver](https://docs.docker.com/engine/admin/logging/overview/). Also note that the default json-file logging driver is not ideally suited for production use.


#### Configuring [Elasticsearch settings](https://www.elastic.co/guide/en/elasticsearch/reference/2.1/setup-configuration.html#settings):

This can be done in two ways.

- create your own `elasticsearch.yml` conf file and override the one shipped by the image using `-v local_elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml`

- pass the parameters as docker env vars via the cli. Examples:

  `docker run -d --memory=4g -v esdatavolume:/usr/share/elasticsearch/data -e ES_JAVA_OPTS="-Xms2g -Xms2g" $ELASTIC_REG/elasticsearch:5.0.0-alpha5`

The image exposes the ports 9200 and 9300.

## Supported Docker versions

The images have been tested on Docker 1.12.

## Contributing, issues and testing

This image is built on top of `container-registry.elastic.co/elasticsearch-ci-base:latest` and is based on [alpine:latest](https://hub.docker.com/_/alpine/).
The complete set of Elasticsearch tests is [regularly executed](https://elasticsearch-ci.elastic.co/view/Elasticsearch/job/elastic+elasticsearch+master+dockeralpine-periodic/) against it.

To report issues, please open an issue in GitHub.

To contribute, please fork and create a PR. Please ensure that tests pass by running `make single-node-test` and `make cluster-unicast-test` first. Test require [docker-compose](https://docs.docker.com/compose/install/)

## Known issues

The following netty4 INFO message can be safely ignored. This [netty4.1 PR](https://github.com/netty/netty/pull/5624) will make this message go away in the future.


> `[INFO ][io.netty.util.internal.PlatformDependent] Your platform does not provide complete low-level API for accessing direct buffers reliably. Unless explicitly requested, heap buffer will always be preferred to avoid potential system unstability.`
