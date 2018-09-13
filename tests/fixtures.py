from .conftest import pytest_configure, pytest_unconfigure
from pytest import config, fixture
from retrying import retry
import requests
from requests import codes
from requests.auth import HTTPBasicAuth
from subprocess import run, PIPE
from .toolbelt import exec_privilege_escalated_command, delete_dir, create_empty_dir
import json
import os
import pytest

retry_settings = {
    'stop_max_delay': 60000,
    'wait_exponential_multiplier': 100,
    'wait_exponential_max': 10000
}

default_index = 'testdata'
http_api_headers = {'Content-Type': 'application/json'}


@fixture()
def elasticsearch(host):
    class Elasticsearch():
        bootstrap_pwd = "pleasechangeme"

        def __init__(self):
            self.version = run('./bin/elastic-version', stdout=PIPE).stdout.decode().strip()
            self.flavor = pytest.config.getoption('--image-flavor')
            self.url = 'http://localhost:9200'

            if config.getoption('--image-flavor') == 'platinum':
                self.auth = HTTPBasicAuth('elastic', Elasticsearch.bootstrap_pwd)
            else:
                self.auth = ''

            if 'STAGING_BUILD_NUM' in os.environ:
                self.tag = '%s-%s' % (self.version, os.environ['STAGING_BUILD_NUM'])
            else:
                self.tag = self.version

            if self.flavor != 'full':
                self.image = 'docker.elastic.co/elasticsearch/elasticsearch-%s:%s' % (self.flavor, self.tag)
            else:
                self.image = 'docker.elastic.co/elasticsearch/elasticsearch:%s' % (self.tag)

            self.docker_metadata = json.loads(
                run(['docker', 'inspect', self.image], stdout=PIPE).stdout.decode())[0]

            self.assert_healthy()

            self.process = host.process.get(comm='java')

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
            return requests.put(self.url + location, headers=http_api_headers, auth=self.auth, **kwargs)

        @retry(**retry_settings)
        def post(self, location='/%s/1' % default_index, **kwargs):
            return requests.post(self.url + location, headers=http_api_headers, auth=self.auth, **kwargs)

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

        def get_node_plugins(self):
            """Return an array of node plugins"""
            nodes = self.get('/_nodes/plugins').json()['nodes'].values()
            return [node['plugins'] for node in nodes]

        def get_node_thread_pool_search_queue_size(self):
            """Return an array of thread_pool search queue size settings for nodes"""
            nodes = self.get('/_nodes?filter_path=**.thread_pool').json()['nodes'].values()
            return [node['settings']['thread_pool']['search']['queue_size'] for node in nodes]

        def get_processors_setting(self):
            nodes = self.get('/_nodes/settings?filter_path=**.processors').json()['nodes'].values()
            return [node['settings']['processors'] for node in nodes]

        def get_node_jvm_stats(self):
            """Return an array of node JVM statistics"""
            nodes = self.get('/_nodes/stats/jvm').json()['nodes'].values()
            return [node['jvm'] for node in nodes]

        def get_node_mlockall_state(self):
            """Return an array of the mlockall value"""
            nodes = self.get('/_nodes?filter_path=**.mlockall').json()['nodes'].values()
            return [node['process']['mlockall'] for node in nodes]

        @retry(**retry_settings)
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
            return self.post(
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
            uninstall_output = host.run(' '.join(["bin/elasticsearch-plugin",
                                                  "-s",
                                                  "remove",
                                                  "{}".format(plugin_name)]))
            # Reset elasticsearch to its original state
            self.reset()
            return uninstall_output

        def assert_bind_mount_data_dir_is_writable(self,
                                                   datadir1="tests/datadir1",
                                                   datadir2="tests/datadir2",
                                                   process_uid='',
                                                   datadir_uid=1000,
                                                   datadir_gid=0):
            cwd = os.getcwd()
            (datavolume1_path, datavolume2_path) = (os.path.join(cwd, datadir1),
                                                    os.path.join(cwd, datadir2))
            config.option.mount_datavolume1 = datavolume1_path
            config.option.mount_datavolume2 = datavolume2_path
            # Yaml variables in docker-compose (`user:`) need to be a strings
            config.option.process_uid = "{!s}".format(process_uid)

            # Ensure defined data dirs are empty before tests
            proc1 = delete_dir(datavolume1_path)
            proc2 = delete_dir(datavolume2_path)

            assert proc1.returncode == 0
            assert proc2.returncode == 0

            create_empty_dir(datavolume1_path, datadir_uid, datadir_gid)
            create_empty_dir(datavolume2_path, datadir_uid, datadir_gid)

            # Force Elasticsearch to re-run with new parameters
            self.reset()
            self.assert_healthy()

            # Revert Elasticsearch back to its datadir defaults for the next tests
            config.option.mount_datavolume1 = None
            config.option.mount_datavolume2 = None
            config.option.process_uid = ''

            self.reset()

            # Finally clean up the temp dirs used for bind-mounts
            delete_dir(datavolume1_path)
            delete_dir(datavolume2_path)

        def es_cmdline(self):
            return host.file("/proc/1/cmdline").content_string

        def run_command_on_host(self, command):
            return host.run(command)

        def get_hostname(self):
            return host.run('hostname').stdout.strip()

        def get_docker_log(self):
            proc = run(['docker-compose',
                        '-f',
                        'docker-compose-{}.yml'.format(config.getoption('--image-flavor')),
                        'logs',
                        self.get_hostname()],
                       stdout=PIPE)
            return proc.stdout.decode()

        def assert_in_docker_log(self, string):
            log = self.get_docker_log()
            try:
                assert string in log
            except AssertionError:
                print(log)
                raise

        def assert_not_in_docker_log(self, string):
            log = self.get_docker_log()
            try:
                assert string not in log
            except AssertionError:
                print(log)
                raise

    return Elasticsearch()
