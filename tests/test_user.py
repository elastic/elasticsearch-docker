from .fixtures import elasticsearch


def test_group_properties(host, elasticsearch):
    group = host.group('elasticsearch')
    assert group.exists
    assert group.gid == 1000


def test_user_properties(host, elasticsearch):
    user = host.user('elasticsearch')
    assert user.uid == 1000
    assert user.gid == 1000
    assert user.home == '/usr/share/elasticsearch'
    assert user.shell == '/bin/bash'
