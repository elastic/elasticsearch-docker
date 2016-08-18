import requests
from retrying import retry
from pytest import fixture


class DockerStackError(Exception):
    pass


def cluster_health():
    response = requests.get(
        "http://elasticsearch:9200/_cluster/health").json()
    return response


def query_all():
    response = requests.get(
        "http://elasticsearch:9200/simpleindex/_search").json()
    return response


def delete_index():
    response = requests.delete(
        "http://elasticsearch:9200/simpleindex/",
        params={"refresh": "true"}).json()
    return response


def create_index():
    index_url = 'http://elasticsearch:9200/simpleindex/testdata/1'
    if requests.get(index_url).status_code != 200:
        requests.post(
            index_url,
            data=open('tests/testdata.json').read(),
            params={"refresh": "true"}
        )


@retry(stop_max_attempt_number=8, wait_exponential_multiplier=100)
def wait_for_cluster_health(desired_state):
    health = cluster_health()
    if health['status'] != desired_state:
        raise DockerStackError(
            "Elasticsearch cluster health is not: '%s'".format(desired_state))


@retry(stop_max_attempt_number=8, wait_exponential_multiplier=100)
def wait_for_elasticsearch():
    try:
        reply = requests.get('http://elasticsearch:9200')
    except requests.ConnectionError:
        raise DockerStackError("Elasticsearch is not answering.")

    status = reply.status_code
    if status != 200:
        raise DockerStackError("Elasticsearch returned HTTP %d." % status)

    cluster_name = reply.json()['cluster_name']
    if cluster_name != 'docker-cluster':
        raise DockerStackError(
            "Elasticsearch cluster has the wrong name: '%s'." % cluster_name)


def setup_elasticsearch():
    wait_for_elasticsearch()
    delete_index()  # Ensure a clean start
    create_index()

@fixture
def docker_stack_uninitialized():
    """Ensure the Docker stack is up and available for testing without data"""
    wait_for_elasticsearch()

@fixture
def docker_stack():
    """Ensure the Docker stack is up and available for testing with basic test data preloaded"""
    setup_elasticsearch()
