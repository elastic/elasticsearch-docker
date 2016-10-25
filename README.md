## Description

This is the official Elasticsearch image created by Elastic Inc.
Elasticsearch is built with [x-pack](https://www.elastic.co/guide/en/x-pack/current/index.html).

## Image tags and hosting

The image is hosted in Elastic's own docker registry: `docker.elastic.co/elasticsearch`

Available tags:

- 5.0.0-beta1
- 5.0.0-rc1
- latest -> 5.0.0-rc1

## Host Prerequisites

### Linux

`vm.max_map_count` sysctl must be set to at least `262144`

This needs to be set permanently in /etc/sysctl.conf:

``` shell
$ grep vm.max_map_count /etc/sysctl.conf
vm.max_map_count=262144
```

And apply the setting using: `sysctl -w vm.max_map_count=262144`

### OSX with [Docker for Mac](https://docs.docker.com/engine/installation/mac/#/docker-for-mac)

The `vm_max_map_count` setting must be set within the xhyve virtual machine:

```shell
$ screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
```

Log in with 'root' and no password.
Then configure the `sysctl` setting as you would for Linux:

```shell
sysctl -w vm.max_map_count=262144
```

### OSX with [Docker Toolbox](https://docs.docker.com/engine/installation/mac/#docker-toolbox)

The sysctl value needs to be set via docker-machine:

``` shell
docker-machine ssh
sudo sysctl -w vm.max_map_count=262144
```

## Using the image

To save some keystrokes first set:

``` shell
export ELASTIC_REG=docker.elastic.co/elasticsearch

```

### Single node example

##### Run instance listening on localhost port 9200:

``` shell
docker run -d -p 9200:9200 -v esdatavolume:/usr/share/elasticsearch/data $ELASTIC_REG/elasticsearch
```

This example uses a [Docker named volume](https://docs.docker.com/engine/tutorials/dockervolumes/) called `esdatavolume` which will be created if not present.

### Cluster example

##### Form a cluster with two instances, `elasticsearch1` listening on `localhost:9200`, `elasticsearch2` on random localhost port:

*WARNING: You need to explicitly set [discovery.zen.minimum_master_nodes](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery-zen.html)*


``` shell
docker run -d -p 9200:9200 -e "discovery.zen.minimum_master_nodes=2" -v esdatavolume1:/usr/share/elasticsearch/data --name elasticsearch1 $ELASTIC_REG/elasticsearch
```

``` shell
docker run -d -P -e "discovery.zen.minimum_master_nodes=2" -e "discovery.zen.ping.unicast.hosts=elasticsearch1" -v esdatavolume2:/usr/share/elasticsearch/data --name elasticsearch2 --link elasticsearch1 $ELASTIC_REG/elasticsearch
```

### Security note

Note that [x-pack](https://www.elastic.co/guide/en/x-pack/current/index.html) is preinstalled in this image.
Please take a few minutes to familiarize yourself with the [x-pack security](https://www.elastic.co/guide/en/x-pack/current/security-getting-started.html) and how to change default passwords. The default password for the `elastic` user is `changeme`.

###### Inspect status of cluster:


```shell
curl -u elastic http://127.0.0.1:9200/_cat/health
Enter host password for user 'elastic':
1472225929 15:38:49 docker-cluster green 2 2 4 2 0 0 0 0 - 100.0%
```

### Logging

Elasticsearch logs go to the console.

### Notes for production use and defaults

1. Defining [elasticsearch parameters](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration.html#settings) can be done with one of the following methods:

  - Create your own `custom_elasticsearch.yml` and override the default shipped with the image using `-v custom_elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml`
  - Present the parameters via docker environment variables.
    For example to define the cluster name with docker run you'd need to pass `-e "cluster.name=mynewclustername"`. Double quotes are required.

    Note that there is a difference in defining [default settings](https://www.elastic.co/guide/en/elasticsearch/reference/5.0/settings.html#_setting_default_settings) and normal settings. The former are prefixed with `default.` and can not override normal settings, if defined.
  - Override the default [CMD](https://docs.docker.com/engine/reference/run/#cmd-default-command-or-options).
    For example to define the cluster name you'd type: `docker run <various parameters> bin/elasticsearch -Ecluster.name=mynewclustername`

2. It is important to correctly set capabilities and ulimits via Docker cli. The following are required, also see [docker-compose.yml](https://github.com/elastic/elasticsearch-docker/blob/master/docker-compose.yml):
   `--cap-add=IPC_LOCK --ulimit memlock=-1:-1 --ulimit nofile=65536:65536`.

   Also ensure `bootstrap.memory_lock` is set to `true` as explained in the [Elasticsearch Docs](https://www.elastic.co/guide/en/elasticsearch/reference/5.0/setup-configuration-memory.html#mlockall). This can be achieved as shown in 1. e.g. by setting the env var `-e "bootstrap.memory_lock=true"`.

3. Define [discovery.zen.minimum_master_nodes](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery-zen.html) based on your requirements.

4. The image [exposes](https://docs.docker.com/engine/reference/builder/#/expose) ports 9200 and 9300. For clusters it is recommended to randomize the listening ports with `--publish-all`, unless you are pinning one container per host

5. Use the env var `ES_JAVA_OPTS` to set heap size, e.g. to use 16GB use `-e ES_JAVA_OPTS="-Xms16g -Xmx16g"` with `docker run`. It is also recommended to set a memory limit for the container.

6. It is recommended to pin your deployments to a specific version of the Elasticsearch Docker image, especially if you are using an orchestration framework like Kubernetes, Amazon ECS or Docker Swarm.

7. Always use a volume bound on `/usr/share/elasticsearch/data`, as shown in the examples, for the following reasons:

  - The data of your elasticsearch node won't be lost if the container gets killed
  - Elasticsearch is IO sensitive and you should not be using the Docker Storage Driver
  - Allows the use of advanced [Docker volume plugins](https://docs.docker.com/engine/extend/plugins/#volume-plugins)

8. If you are using the devicemapper storage driver (default at least on RedHat (rpm) based distributions) make sure you are not using the default `loop-lvm` mode but [configure docker-engine](https://docs.docker.com/engine/userguide/storagedriver/device-mapper-driver/#configure-docker-with-devicemapper) to use direct-lvm instead.

9. Consider centralizing your logs by using a different [logging driver](https://docs.docker.com/engine/admin/logging/overview/). Also note that the default json-file logging driver is not ideally suited for production use.


## Supported Docker versions

The images have been tested on Docker 1.12.1.

## Contributing, issues and testing

This image is built on top of [elasticsearch-alpine-base](https://github.com/elastic/elasticsearch-alpine-base) and is based on [alpine:latest](https://hub.docker.com/_/alpine/).
The complete set of Elasticsearch tests is [regularly executed](https://elasticsearch-ci.elastic.co/view/Elasticsearch/job/elastic+elasticsearch+master+dockeralpine-periodic/) against it.

To report issues, please open an issue in [GitHub](https://github.com/elastic/elasticsearch-docker/issues).

To contribute, please fork and create a PR. Please ensure that tests pass by running `make acceptance-test`. Tests require [docker-compose](https://docs.docker.com/compose/install/).

## Known issues

The following netty4 INFO message can be safely ignored. This [netty4.1 PR](https://github.com/netty/netty/pull/5624) will make this message go away in the future.


> `[INFO ][io.netty.util.internal.PlatformDependent] Your platform does not provide complete low-level API for accessing direct buffers reliably. Unless explicitly requested, heap buffer will always be preferred to avoid potential system unstability.`
