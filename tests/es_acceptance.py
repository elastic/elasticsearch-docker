import requests
from requests.auth import HTTPBasicAuth
from retrying import retry
from pytest import fixture


class DockerStackError(Exception):
    pass


class SecurityError(Exception):
    pass

admin_username = 'elastic'
admin_defaultpwd = 'changeme'
admin_newpwd = 'testpassword'


def cluster_health():
    response = requests.get(
        "http://elasticsearch:9200/_cluster/health",
        auth=HTTPBasicAuth(admin_username, admin_newpwd)).json()
    return response


def query_all():
    response = requests.get(
        "http://elasticsearch:9200/simpleindex/_search",
        auth=HTTPBasicAuth(admin_username, admin_newpwd)).json()
    return response


def delete_index():
    response = requests.delete(
        "http://elasticsearch:9200/simpleindex/",
        auth=HTTPBasicAuth(admin_username, admin_newpwd)).json()
    requests.post('http://elasticsearch:9200/_refresh/',)
    return response


def create_index():
    index_url = 'http://elasticsearch:9200/simpleindex/testdata/1'
    response = requests.get(
        index_url,
        auth=HTTPBasicAuth(admin_username, admin_newpwd))

    if response.status_code != 200:
        requests.post(
            index_url,
            data=open('tests/testdata.json').read(),
            params={"refresh": "true"},
            auth=HTTPBasicAuth(admin_username, admin_newpwd))


@retry(stop_max_attempt_number=8, wait_exponential_multiplier=100, wait_exponential_max=60000)
def wait_for_cluster_health(desired_state):
    health = cluster_health()
    if health['status'] != desired_state:
        raise DockerStackError(
            "Elasticsearch cluster health is not: '{}'".format(desired_state))


@retry(stop_max_attempt_number=8, wait_exponential_multiplier=400, wait_exponential_max=60000)
def wait_for_elasticsearch(xpack=False, admin_username = admin_username, admin_pwd = admin_defaultpwd):
    try:
        if xpack is True:
            reply = requests.get(
                "http://elasticsearch:9200/_cluster/health",
                auth=HTTPBasicAuth(admin_username, admin_pwd))
        else:
            reply = requests.get('http://elasticsearch:9200')
    except requests.ConnectionError:
        raise DockerStackError("Elasticsearch is not answering.")

    status = reply.status_code

    if status != 200:
        raise DockerStackError("Elasticsearch returned HTTP {}.".format(status), status)

    cluster_name = reply.json()['cluster_name']
    if cluster_name != 'docker-cluster':
        raise DockerStackError(
            "Elasticsearch cluster has the wrong name: '{}'.".format(cluster_name))


def change_default_elastic_password():
    reply = requests.put('http://elasticsearch:9200/_xpack/security/user/{}/_password'.format(admin_username),
                         json={"password": admin_newpwd},
                         auth=HTTPBasicAuth(admin_username, admin_defaultpwd))

    status = reply.status_code

    if status != 200:
        raise SecurityError("Elasticsearch returned HTTP {} while trying to change default password.".format(status))

    return status


def setup_elasticsearch():
    delete_index()  # Ensure a clean start
    create_index()


@fixture
def docker_stack_uninitialized():
    """Ensure the Docker stack is up and available for testing without data"""
    wait_for_elasticsearch()

@fixture
def docker_xpack_stack_uninitialized():
    """Ensure the Docker stack is up and available for testing without data"""
    wait_for_elasticsearch(xpack=True)


@fixture
def docker_stack():
    """Ensure the Docker stack is up and available for testing with basic test data preloaded"""
    setup_elasticsearch()
