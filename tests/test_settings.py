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
    # The number of bytes that we assert is not exactly what we
    # specify in the fixture. This is due to jvm honoring the
    # generation and survivor ratios, rounding and alignments.  It is
    # enough if Elasticsearch reports a max heap size within 64MB of
    # the target value set in the fixture (=1152MB).

    mem_delta_mb = 64
    for jvm in elasticsearch.get_node_jvm_stats():
        reported_heap_max_in_mb = int(jvm['mem']['heap_max_in_bytes'] / (1024**2))
        assert abs(reported_heap_max_in_mb - 1152) < mem_delta_mb


def test_envar_not_including_a_dot_is_not_presented_to_elasticsearch(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml
    assert 'irrelevantsetting' not in elasticsearch.es_cmdline()


def test_capitalized_envvar_is_not_presented_to_elasticsearch(elasticsearch):
    # The fixture for this test comes from tests/docker-compose.yml
    assert 'NonESRelatedVariable' not in elasticsearch.es_cmdline()
