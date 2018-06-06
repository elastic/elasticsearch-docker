from .fixtures import elasticsearch


def test_labels(elasticsearch):
    labels = elasticsearch.docker_metadata['Config']['Labels']
    assert labels['org.label-schema.name'] == 'elasticsearch'
    assert labels['org.label-schema.schema-version'] == '1.0'
    assert labels['org.label-schema.url'] == 'https://www.elastic.co/products/elasticsearch'
    assert labels['org.label-schema.vcs-url'] == 'https://github.com/elastic/elasticsearch-docker'
    assert labels['org.label-schema.vendor'] == 'Elastic'
    assert labels['org.label-schema.version'] == elasticsearch.tag
    if elasticsearch.flavor == 'oss':
        assert labels['license'] == 'Apache-2.0'
    else:
        assert labels['license'] == 'Elastic License'
