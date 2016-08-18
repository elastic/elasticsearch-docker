from __future__ import print_function
from es_acceptance import docker_stack, docker_stack_uninitialized
from es_acceptance import cluster_health, query_all, delete_index, create_index, wait_for_cluster_health
from pytest import fixture


# state should be green on first run regardless of no. of nodes
def test_cluster_health(docker_stack_uninitialized):
    health = cluster_health()
    assert "green" == health['status']


def test_create_basic_index(docker_stack):
    hits = query_all()['hits']['hits']
    assert "lorem" in hits[0]['_source'].values()
    assert "ipsum" in hits[0]['_source'].values()


def test_delete_basic_index(docker_stack):
    delete_result = delete_index()
    assert {'acknowledged': True} == delete_result


def test_fail_search_on_nonexistent_index(docker_stack):
    delete_index()
    error_root_cause = query_all()['error']['root_cause']
    assert "no such index" == error_root_cause[0]['reason']
    assert "simpleindex" == error_root_cause[0]['index']


def test_cluster_health_after_crud(docker_stack):
    health = cluster_health()
    # health will be yellow on single node cluster after data has been inserted
    if health['number_of_nodes'] == 1:
        wait_for_cluster_health('yellow')
        # TODO convert ^^ to an assert
    else:
        wait_for_cluster_health('green')

    delete_index()
    # and back to green for all clusters with no data
    health = cluster_health()
    wait_for_cluster_health('green')
