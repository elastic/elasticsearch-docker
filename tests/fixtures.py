import json
from pytest import fixture
from retrying import retry

retry_settings = {
    'stop_max_attempt_number': 8,
    'wait_exponential_multiplier': 100,
    'wait_exponential_max': 60000
}


@fixture()
def elasticsearch(Process, Command):
    class Elasticsearch:
        def __init__(self):
            self.process = Process.get(comm='java')

        @retry(**retry_settings)
        def get(self, location='/'):
            return Command.check_output(
                'curl -s http://elastic:changeme@localhost:9200%s' % location)

        def get_node_info(self):
            return json.loads(self.get())

    return Elasticsearch()
