from subprocess import run
from os import environ


def pytest_configure(config):
    containers = ['elasticsearch1', 'elasticsearch2']
    environ['ES_NODE_COUNT'] = str(len(containers))
    compose_flags = '-f docker-compose.yml -f docker-compose.hostports.yml up -d'.split(' ')
    run(['docker-compose'] + compose_flags + containers)


def pytest_unconfigure(config):
    run(['docker-compose', 'down', '-v'])
    run(['docker-compose', 'rm', '-f', '-v'])
