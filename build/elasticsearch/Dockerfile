FROM docker.elastic.co/elasticsearch/elasticsearch-alpine-base:latest
MAINTAINER Elastic Docker Team <docker@elastic.co>

ARG ELASTICSEARCH_VERSION
ENV PATH /usr/share/elasticsearch/bin:$PATH
ENV JAVA_HOME /usr/lib/jvm/java-1.8-openjdk

WORKDIR /usr/share/elasticsearch

# Download/extract defined ES version. busybox tar can't strip leading dir.
# Working with RC 5.0.0-beta1 candidates for now
RUN wget http://staging.elastic.co/${ELASTICSEARCH_VERSION}-5eb5cbdb/downloads/elasticsearch/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz && \
    EXPECTED_SHA=$(wget -O - http://staging.elastic.co/${ELASTICSEARCH_VERSION}-5eb5cbdb/downloads/elasticsearch/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz.sha1) && \
    test $EXPECTED_SHA == $(sha1sum elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz | awk '{print $1}') && \
    tar zxf elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz && \
    chown -R elasticsearch:elasticsearch elasticsearch-${ELASTICSEARCH_VERSION} && \
    mv elasticsearch-${ELASTICSEARCH_VERSION}/* . && \
    rmdir elasticsearch-${ELASTICSEARCH_VERSION} && \
    rm elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz

RUN set -ex && for esdirs in config data logs; do \
        mkdir -p "$esdirs"; \
        chown -R elasticsearch:elasticsearch "$esdirs"; \
    done

COPY elasticsearch.yml /usr/share/elasticsearch/config/
RUN chown elasticsearch:elasticsearch /usr/share/elasticsearch/config/elasticsearch.yml

USER elasticsearch

# Install xpack
#RUN elasticsearch-plugin install --batch x-pack
# Working with RC 5.0.0-beta1 candidates for now
RUN ES_JAVA_OPTS="-Des.plugins.staging=5eb5cbdb" bin/elasticsearch-plugin install --batch x-pack

COPY elasticsearch.yml /usr/share/elasticsearch/config/
COPY log4j2.properties /usr/share/elasticsearch/config/

CMD ["/bin/sh", "bin/elasticsearch"]

EXPOSE 9200 9300
