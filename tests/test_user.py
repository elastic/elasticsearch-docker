from .fixtures import elasticsearch


def test_group_properties(Group, elasticsearch):
    group = Group('elasticsearch')
    assert group.exists
    assert group.gid == 1000


def test_user_properties(User, elasticsearch):
    user = User('elasticsearch')
    assert user.uid == 1000
    assert user.gid == 1000
    assert user.home == '/usr/share/elasticsearch'
    assert user.shell == '/bin/bash'
