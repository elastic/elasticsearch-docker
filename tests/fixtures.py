from .conftest import pytest_configure, pytest_unconfigure
from pytest import config, fixture
from retrying import retry
import requests
from requests import codes
from requests.auth import HTTPBasicAuth
from .helpers import filter_dict_by_parent_and_child_key

retry_settings = {
    'stop_max_delay': 30000,
    'wait_exponential_multiplier': 100,
    'wait_exponential_max': 10000
}

default_index = 'testdata'


@fixture()
def elasticsearch(Process, Command, File):
    class Elasticsearch:
        def __init__(self):
            self.url = 'http://localhost:9200'
            self.auth = HTTPBasicAuth('elastic', 'changeme')

            self.assert_healthy()
            self.process = Process.get(comm='java')

            # Retain a handle to the Command fixture letting us execute commands within the container(s)
            self.command = Command

            # Retain a handle to the File fixture letting us check files inside the container(s)
            self.localfile = File

            # Start each test with a clean slate.
            assert self.load_index_template().status_code == codes.ok
            assert self.delete().status_code == codes.ok

        def reset(self):
            """Reset Elasticsearch by destroying and recreating the containers."""
            pytest_unconfigure(config)
            pytest_configure(config)

        @retry(**retry_settings)
        def get(self, location='/', **kwargs):
            return requests.get(self.url + location, auth=self.auth, **kwargs)

        @retry(**retry_settings)
        def put(self, location='/', **kwargs):
            return requests.put(self.url + location, auth=self.auth, **kwargs)

        @retry(**retry_settings)
        def post(self, location='/%s/1' % default_index, **kwargs):
            return requests.post(self.url + location, auth=self.auth, **kwargs)

        @retry(**retry_settings)
        def delete(self, location='/_all', **kwargs):
            return requests.delete(self.url + location, auth=self.auth, **kwargs)

        def get_root_page(self):
            return self.get('/').json()

        def get_cluster_health(self):
            return self.get('/_cluster/health').json()

        def get_node_count(self):
            return self.get_cluster_health()['number_of_nodes']

        def get_cluster_status(self):
            return self.get_cluster_health()['status']

        def get_node_os_stats(self):
            """Return an array of node OS statistics"""
            return self.get('/_nodes/stats/os').json()['nodes'].values()

        def get_nodes_heap_max_in_bytes(self):
            """Return an array with jvm mem stats"""
            return filter_dict_by_parent_and_child_key(self.get('/_nodes/stats/jvm').json(),
                                                       'jvm',
                                                       'mem',
                                                       'heap_max_in_bytes')

        def set_password(self, username, password):
            return self.put('/_xpack/security/user/%s/_password' % username,
                            json={"password": password})

        def query_all(self, index=default_index):
            return self.get('/%s/_search' % index)

        def create_index(self, index=default_index):
            return self.put('/' + index)

        def delete_index(self, index=default_index):
            return self.delete('/' + index)

        def load_index_template(self):
            template = {
                'template': '*',
                'settings': {
                    'number_of_shards': 2,
                    'number_of_replicas': 0,
                }
            }
            return self.put('/_template/univeral_template', json=template)

        def load_test_data(self):
            self.create_index()
            self.post(
                data=open('tests/testdata.json').read(),
                params={"refresh": "wait_for"}
            )

        @retry(**retry_settings)
        def assert_healthy(self):
            if config.getoption('--single-node'):
                assert self.get_node_count() == 1
                assert self.get_cluster_status() in ['yellow', 'green']
            else:
                assert self.get_node_count() == 2
                assert self.get_cluster_status() == 'green'

        def uninstall_plugin(self, plugin_name):
            # This will run on only one host, but this is ok for the moment
            # TODO: as per http://testinfra.readthedocs.io/en/latest/examples.html#test-docker-images
            uninstall_output = self.command.run(' '.join(["bin/elasticsearch-plugin",
                                                          "-s",
                                                          "remove",
                                                          "{}".format(plugin_name)]))
            # Reset elasticsearch to its original state
            self.reset()
            return uninstall_output

        def es_cmdline(self):
            return self.localfile("/proc/1/cmdline").content_string

    return Elasticsearch()
