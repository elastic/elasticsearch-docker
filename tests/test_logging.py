from .fixtures import elasticsearch
import pytest

image_flavor = pytest.config.getoption('--image-flavor')


def test_elasticsearch_logs_are_in_docker_logs(elasticsearch):
    elasticsearch.assert_in_docker_log('o.e.n.Node')
    # eg. elasticsearch1 | [2017-07-04T00:54:22,604][INFO ][o.e.n.Node  ] [docker-test-node-1] initializing ...


def test_info_level_logs_are_in_docker_logs(elasticsearch):
    elasticsearch.assert_in_docker_log('INFO')
