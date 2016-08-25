## Description

This is the official Elasticsearch image created by Elastic Inc.

## Image tags and hosting

The image is hosted in Elastic's own docker registry: `container-registry.elastic.co/elasticsearch`

Available tags:

- 5.0.0-alpha5
- latest -> 5.0.0-alpha5

## Host Prerequisites

### Linux

`vm.max_map_count` sysctl must be set to at least `262144`

This needs to be set permanently in /etc/sysctl.conf:

``` shell
$ grep vm.max_map_count /etc/sysctl.conf
vm.max_map_count=262144
```

And apply the setting using: `sysctl -w vm.max_map_count=262144`

## Using the image

To save some keystrokes first set:

``` shell
export ELASTIC_REG=container-registry.elastic.co/elasticsearch

```

### Single node example

##### Run instance listening on localhost port 9200:

``` shell
docker run -d -p 9200:9200 -v esdatavolume:/usr/share/elasticsearch/data $ELASTIC_REG/elasticsearch:5.0.0-alpha5
```

This example uses a [Docker named volume](https://docs.docker.com/engine/tutorials/dockervolumes/) called `esdatavolume` which will be created if not present.

### Cluster example

##### Form a cluster with two instances, `elasticsearch1` listening on `localhost:9200`, `elasticsearch2` on random localhost port:

*WARNING: You need to explicitly set [discovery.zen.minimum_master_nodes](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery-zen.html)*


``` shell
docker run -d -p 9200:9200 -v esdatavolume1:/usr/share/elasticsearch/data --name elasticsearch1 $ELASTIC_REG/elasticsearch:5.0.0-alpha5 bin/elasticsearch -E discovery.zen.minimum_master_nodes=2
```

``` shell
docker run -d -P -v esdatavolume2:/usr/share/elasticsearch/data --name elasticsearch2 --link elasticsearch1 $ELASTIC_REG/elasticsearch:5.0.0-alpha5 bin/elasticsearch -E discovery.zen.minimum_master_nodes=2 -E discovery.zen.ping.unicast.hosts=elasticsearch1
```

###### Inspect status of cluster:

```shell
curl http://127.0.0.1:9200/_cat/health
1471855299 08:41:39 docker-cluster green 2 2 0 0 0 0 0 0 - 100.0%
```

### Logging

Elasticsearch logs go to the console.

### Notes for production use and defaults

1. It is important to correctly set capabilities and ulimits via Docker cli. The following are required, also see [docker-compose.yml](https://github.com/elastic/elasticsearch-docker/blob/master/docker-compose.yml):
   `--cap-add=IPC_LOCK --ulimit memlock=-1:-1 --ulimit nofile=65536:65536`

2. Define [discovery.zen.minimum_master_nodes](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery-zen.html) based on your requirements

3. The image [exposes](https://docs.docker.com/engine/reference/builder/#/expose) ports 9200 and 9300. For clusters it is recommended to randomize the listening ports with `--publish-all`, unless you are pinning one container per host

4. Use the env var `ES_JAVA_OPTS` to set heap size, e.g. to use 16GB use `-e ES_JAVA_OPTS="-Xms16g -Xmx=16g"` with `docker run`. It is also recommended to set a memory limit for the container.

5. It is recommended to pin your deployments to a specific version of the Elasticsearch Docker image, especially if you are using an orchestration framework like Kubernetes, Amazon ECS or Docker Swarm.

6. Always use a volume bound on `/usr/share/elasticsearch/data`, as shown in the examples, for the following reasons:

  - The data of your elasticsearch node won't be lost if the container gets killed
  - Elasticsearch is IO sensitive and you should not be using the Docker Storage Driver
  - Allows the use of advanced [Docker volume plugins](https://docs.docker.com/engine/extend/plugins/#volume-plugins)

7. Consider centralizing your logs by using a different [logging driver](https://docs.docker.com/engine/admin/logging/overview/). Also note that the default json-file logging driver is not ideally suited for production use.


#### Configuring [Elasticsearch settings](https://www.elastic.co/guide/en/elasticsearch/reference/2.1/setup-configuration.html#settings):

This can be done in two ways.

- create your own `custom_elasticsearch.yml` conf file and override the one shipped by the image using `-v custom_elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml`

- pass the parameters as docker env vars via the cli. Examples:

  `docker run -d --memory=4g -v esdatavolume:/usr/share/elasticsearch/data -e ES_JAVA_OPTS="-Xms2g -Xms2g" $ELASTIC_REG/elasticsearch:5.0.0-alpha5`

## Supported Docker versions

The images have been tested on Docker 1.12.

## Contributing, issues and testing

This image is built on top of [elasticsearch-alpine-base](https://github.com/elastic/elasticsearch-alpine-base) and is based on [alpine:latest](https://hub.docker.com/_/alpine/).
The complete set of Elasticsearch tests is [regularly executed](https://elasticsearch-ci.elastic.co/view/Elasticsearch/job/elastic+elasticsearch+master+dockeralpine-periodic/) against it.

To report issues, please open an issue in [GitHub](https://github.com/elastic/elasticsearch-docker/issues).

To contribute, please fork and create a PR. Please ensure that tests pass by running `make acceptance-test`. Tests require [docker-compose](https://docs.docker.com/compose/install/).

## Known issues

The following netty4 INFO message can be safely ignored. This [netty4.1 PR](https://github.com/netty/netty/pull/5624) will make this message go away in the future.


> `[INFO ][io.netty.util.internal.PlatformDependent] Your platform does not provide complete low-level API for accessing direct buffers reliably. Unless explicitly requested, heap buffer will always be preferred to avoid potential system unstability.`
