FROM container-registry.elastic.co/elasticsearch/elasticsearch-ci-base:latest
ARG ELASTICSEARCH_VERSION
ENV PATH /usr/share/elasticsearch/bin:$PATH
ENV JAVA_HOME /usr/lib/jvm/java-1.8-openjdk

WORKDIR /usr/share/elasticsearch

# Download/extract defined ES version. busybox tar can't strip leading dir.
RUN wget http://repo1.maven.org/maven2/org/elasticsearch/distribution/tar/elasticsearch/${ELASTICSEARCH_VERSION}/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz && \
    EXPECTED_SHA=$(wget -O - http://repo1.maven.org/maven2/org/elasticsearch/distribution/tar/elasticsearch/${ELASTICSEARCH_VERSION}/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz.sha1) && \
    test $EXPECTED_SHA == $(sha1sum elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz | awk '{print $1}') && \
    tar zxf elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz && \
    chown -R elasticsearch:elasticsearch elasticsearch-${ELASTICSEARCH_VERSION} && \
    mv elasticsearch-${ELASTICSEARCH_VERSION}/* . && \
    rmdir elasticsearch-${ELASTICSEARCH_VERSION} && \
    rm elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz
RUN set -ex && for path in data logs config config/scripts; do \
        mkdir -p "$path"; \
        chown -R elasticsearch:elasticsearch "$path"; \
    done
COPY logging.yml /usr/share/elasticsearch/config/
COPY elasticsearch.yml /usr/share/elasticsearch/config/

USER elasticsearch

CMD ["/bin/sh", "bin/elasticsearch"]

EXPOSE 9200 9300
