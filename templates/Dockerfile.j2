################################################################################
# This Dockerfile was generated from the template at templates/Dockerfile.j2
#
# Beginning of multi stage Dockerfile
################################################################################

{% set ingest_plugins = 'ingest-user-agent ingest-geoip' %}
{% set version_tag = elastic_version -%}
{% set tarball = 'elasticsearch-%s.tar.gz' % elastic_version -%}

{% if artifacts_dir -%}
{%   set url_root = 'http://localhost:8000/elasticsearch/distribution/tar/build/distributions' -%}
{%   set x_pack_url_root = 'http://localhost:8000/x-pack-elasticsearch/plugin/build/distributions' -%}
{%   set plugin_url_root = 'http://localhost:8000/elasticsearch/plugins' -%}
{% elif staging_build_num -%}
{%   set version_tag = version_tag + '-' + staging_build_num -%}
{%   set url_root = 'https://staging.elastic.co/%s/downloads/elasticsearch' % version_tag -%}
{% elif elastic_version.endswith('-SNAPSHOT') -%}
{%   set url_root = 'https://snapshots.elastic.co/downloads/elasticsearch' -%}
{% else -%}
{%   set url_root = 'https://artifacts.elastic.co/downloads/elasticsearch' -%}
{% endif -%}

################################################################################
# Build stage 0 `prep_es_files`:
# Extract elasticsearch artifact
# Install required plugins
# Set gid=0 and make group perms==owner perms
################################################################################

FROM centos:7 AS prep_es_files

ENV PATH /usr/share/elasticsearch/bin:$PATH
ENV JAVA_HOME /usr/lib/jvm/jre-1.8.0-openjdk

RUN yum install -y java-1.8.0-openjdk-headless unzip which

RUN groupadd -g 1000 elasticsearch && \
    adduser -u 1000 -g 1000 -d /usr/share/elasticsearch elasticsearch

WORKDIR /usr/share/elasticsearch

USER 1000

# Download and extract defined ES version.
RUN curl -fsSL {{ url_root }}/{{ tarball }} | \
    tar zx --strip-components=1

RUN set -ex && for esdirs in config data logs; do \
        mkdir -p "$esdirs"; \
    done

# Install x-pack and also the ingest-{agent,geoip} modules required for Filebeat
{% if artifacts_dir -%}
  {% if image_flavor != 'oss' -%}
RUN elasticsearch-plugin install --batch "{{ x_pack_url_root }}/x-pack-{{ elastic_version }}.zip"
  {%- endif %}
RUN for PLUGIN in {{ ingest_plugins }}; do \
      elasticsearch-plugin install --batch "{{ plugin_url_root }}/$PLUGIN/build/distributions/$PLUGIN-{{ elastic_version }}.zip"; \
    done
{% elif staging_build_num -%}
  {% if image_flavor != 'oss' -%}
RUN for PLUGIN in x-pack {{ ingest_plugins }}; do \
  {% else -%}
RUN for PLUGIN in {{ ingest_plugins }}; do \
  {%- endif -%}
      eval ES_JAVA_OPTS="-Des.plugins.staging={{ staging_build_num }}" elasticsearch-plugin install --batch "$PLUGIN"; \
    done
{% else -%}
  {% if image_flavor != 'oss' -%}
RUN for PLUGIN in x-pack {{ ingest_plugins }}; do \
  {% else -%}
RUN for PLUGIN in {{ ingest_plugins }}; do \
  {%- endif -%}
      elasticsearch-plugin install --batch "$PLUGIN"; done
{%- endif %}

COPY --chown=1000:0 elasticsearch.yml log4j2.properties config/

{% if image_flavor == 'platinum' -%}
# Enable security logging audit trail
COPY --chown=1000:0 x-pack/log4j2.properties config/x-pack/
RUN echo 'xpack.license.self_generated.type: trial' >>config/elasticsearch.yml

{% elif image_flavor == 'basic' -%}
RUN echo 'xpack.license.self_generated.type: basic' >>config/elasticsearch.yml
{% endif -%}

USER 0

# Set gid to 0 for elasticsearch and make group permission similar to that of user
# This is needed, for example, for Openshift Open: https://docs.openshift.org/latest/creating_images/guidelines.html
# and allows ES to run with an uid
RUN chown -R elasticsearch:0 . && \
    chmod -R g=u /usr/share/elasticsearch

################################################################################
# Build stage 1 (the actual elasticsearch image):
# Copy elasticsearch from stage 0
# Add entrypoint
################################################################################

# Use a centos base that has openjdk-1.8.0.b141 pre-installed and excluded from yum.conf
# until potential issues with build 144 have been troubleshooted
FROM centos:7
LABEL maintainer "Elastic Docker Team <docker@elastic.co>"

ENV ELASTIC_CONTAINER true
ENV PATH /usr/share/elasticsearch/bin:$PATH
ENV JAVA_HOME /usr/lib/jvm/jre-1.8.0-openjdk

RUN yum update -y && \
    yum install -y nc java-1.8.0-openjdk-headless unzip wget which && \
    yum clean all

RUN groupadd -g 1000 elasticsearch && \
    adduser -u 1000 -g 1000 -G 0 -d /usr/share/elasticsearch elasticsearch && \
    chmod 0775 /usr/share/elasticsearch && \
    chgrp 0 /usr/share/elasticsearch

WORKDIR /usr/share/elasticsearch

COPY --from=prep_es_files --chown=1000:0 /usr/share/elasticsearch /usr/share/elasticsearch

COPY --chown=1000:0 bin/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Openshift overrides USER and uses ones with randomly uid>1024 and gid=0
# Allow ENTRYPOINT (and ES) to run even with a different user
RUN chgrp 0 /usr/local/bin/docker-entrypoint.sh && \
    chmod g=u /etc/passwd && \
    chmod 0775 /usr/local/bin/docker-entrypoint.sh

EXPOSE 9200 9300

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
# Dummy overridable parameter parsed by entrypoint
CMD ["eswrapper"]

################################################################################
# End of multi-stage Dockerfile
################################################################################
