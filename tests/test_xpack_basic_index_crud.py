from .fixtures import elasticsearch
from requests import codes
import pytest

image_flavor = pytest.config.getoption('--image-flavor')


def test_create_index(elasticsearch):
    response = elasticsearch.create_index('creation_test_index')
    assert response.status_code == codes.ok
    assert response.json()['acknowledged'] is True
    assert elasticsearch.get('/creation_test_index').status_code == codes.ok


def test_search(elasticsearch):
    response = elasticsearch.load_test_data()
    assert response.status_code == codes.created
    hits = elasticsearch.query_all().json()['hits']['hits']
    assert 'lorem' in hits[0]['_source'].values()
    assert 'ipsum' in hits[0]['_source'].values()


def test_delete_index(elasticsearch):
    elasticsearch.create_index('deletion_test_index')
    response = elasticsearch.delete_index('deletion_test_index')
    assert response.status_code == codes.ok
    assert response.json()['acknowledged'] is True
    assert elasticsearch.get('/deletion_test_index').status_code == codes.not_found


def test_search_on_nonexistent_index_fails(elasticsearch):
    response = elasticsearch.query_all('no_index')
    error_root_cause = response.json()['error']['root_cause'][0]
    assert 'no_index' == error_root_cause['index']
    assert 'no such index [no_index]' == error_root_cause['reason']


def test_cluster_is_healthy_after_indexing_data(elasticsearch):
    elasticsearch.load_test_data()
    elasticsearch.assert_healthy()


def test_cgroup_os_stats_are_available(elasticsearch):
    # Elasticsearch should be capable of returning cgroup stats for all nodes
    for node_stats in elasticsearch.get_node_os_stats():
        assert 'cgroup' in node_stats['os']
        assert 'cpu' in node_stats['os']['cgroup']
        assert 'cpuacct' in node_stats['os']['cgroup']
