from .fixtures import elasticsearch
import pytest


def test_setting_node_name_with_an_environment_variable(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml
    assert elasticsearch.get_root_page()['name'].startswith('docker-test-node')


def test_setting_cluster_name_with_an_environment_variable(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml
    assert elasticsearch.get_root_page()['cluster_name'] == ('docker-test-cluster')


def test_setting_heapsize_with_an_environment_variable(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml.
    #
    # The number of bytes that we assert is not exactly what we specify
    # in the fixture. The exact value would be 1206910976, but due to JVM
    # subtleties, the actual number is lower.
    for jvm in elasticsearch.get_node_jvm_stats():
        assert jvm['mem']['heap_max_in_bytes'] == 1173094400


def test_envar_not_including_a_dot_is_not_presented_to_elasticsearch(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml
    assert 'irrelevantsetting' not in elasticsearch.es_cmdline()


def test_capitalized_envvar_is_not_presented_to_elasticsearch(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml
    assert 'NonESRelatedVariable' not in elasticsearch.es_cmdline()
