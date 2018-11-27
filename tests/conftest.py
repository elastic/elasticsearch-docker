from subprocess import run
import os
import pytest


def pytest_addoption(parser):
    """Customize testinfra with config options via cli args"""

    # By default run tests in clustered mode, but allow dev mode with --single-node"""
    parser.addoption('--single-node', action='store_true',
                     help='non-clustered version')

    # Let us specify which docker-compose-(image_flavor).yml file to use
    parser.addoption('--image-flavor', action='store',
                     help='Docker image flavor; the suffix used in docker-compose-<flavor>.yml')

    # Bind-mount a user specified dir for the data dir
    parser.addoption('--mount-datavolume1', action='store',
                     help='The host dir to be bind-mounted on /usr/share/elasticsearch/data for the first node')
    # Bind-mount a user specified dir for the data dir
    parser.addoption('--mount-datavolume2', action='store',
                     help='The host dir to be bind-mounted on /usr/share/elasticsearch/data for the second node')

    # Let us override the Dockerfile's USER; akin to specifying `--user` in the docker run.
    parser.addoption('--process-uid', action='store',
                     help='Used to override the Dockerfile\'s USER')


def pytest_configure(config):
    # Named volumes used by default for persistence of each container
    (datavolume1, datavolume2) = ("esdata1", "esdata2")
    # Our default is not to override uid; empty strings for --user are ignored by Docker.
    process_uid = ''
    image_flavor = config.getoption('--image-flavor')

    # Use a host dir for the data volume of Elasticsearch, if specified
    if config.getoption('--mount-datavolume1'):
        datavolume1 = config.getoption('--mount-datavolume1')
    if config.getoption('--mount-datavolume2'):
        datavolume2 = config.getoption('--mount-datavolume2')
    if config.getoption('--process-uid'):
        process_uid = config.getoption('--process-uid')

    env_vars = os.environ
    env_vars['DATA_VOLUME1'] = datavolume1
    env_vars['DATA_VOLUME2'] = datavolume2
    env_vars['PROCESS_UID'] = process_uid

    compose_cli = ['docker-compose', '-f', 'docker-compose.yml', 'up', '-d']
    compose_dir = '.tedi/build/elasticsearch-%s' % image_flavor
    if config.getoption('--single-node'):
        compose_cli.append('elasticsearch1')

    startup_result = run(compose_cli, env=env_vars, cwd=compose_dir)
    startup_result.check_returncode()


def pytest_unconfigure(config):
    image_flavor = config.getoption('--image-flavor')
    compose_dir = '.tedi/build/elasticsearch-%s' % image_flavor
    run(['docker-compose', 'down', '-v'], cwd=compose_dir)
    run(['docker-compose', 'rm', '-f', '-v'], cwd=compose_dir)
