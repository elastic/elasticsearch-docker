from .fixtures import elasticsearch


def test_process_is_pid_1(elasticsearch):
    assert elasticsearch.process.pid == 1


def test_process_is_running_as_the_correct_user(elasticsearch):
    assert elasticsearch.process.user == 'elasticsearch'
