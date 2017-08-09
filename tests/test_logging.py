from .fixtures import elasticsearch
import pytest

image_flavor = pytest.config.getoption('--image-flavor')


def test_elasticsearch_logs_are_in_docker_logs(elasticsearch):
    elasticsearch.assert_in_docker_log('o.e.n.Node')
    # eg. elasticsearch1 | [2017-07-04T00:54:22,604][INFO ][o.e.n.Node  ] [docker-test-node-1] initializing ...


@pytest.mark.skipif(image_flavor != 'platinum',
                    reason="x-pack.security not installed in the -{} image.".format(image_flavor))
def test_security_audit_logs_are_in_docker_logs(elasticsearch):
    elasticsearch.assert_in_docker_log('x.s.a.l.LoggingAuditTrail')
    # eg. elasticsearch1 | [2017-07-04T01:10:19,189][INFO ][o.e.x.s.a.l.LoggingAuditTrail] [transport] [access_granted]


def test_info_level_logs_are_in_docker_logs(elasticsearch):
    elasticsearch.assert_in_docker_log('INFO')


def test_no_errors_are_in_docker_logs(elasticsearch):
    elasticsearch.assert_not_in_docker_log('ERROR')
