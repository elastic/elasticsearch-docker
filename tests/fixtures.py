import pytest


@pytest.fixture()
def elasticsearch(Process):
    class Elasticsearch:
        def __init__(self):
            self.process = Process.get(comm='java')

    return Elasticsearch()
