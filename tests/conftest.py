from subprocess import run
import pytest


def pytest_addoption(parser):
    """By default run tests in clustered mode, but allow dev mode with --single-node"""
    parser.addoption('--single-node', action='store_true',
                     help='non-clustered version')
    # Let us specify with docker-compose-(image_flavor) file to use
    parser.addoption('--image-flavor', action='store',
                     help='Docker image flavor; the suffix used in docker-compose-<flavor>.yml')


def pytest_configure(config):
    compose_suffix = config.getoption('--image-flavor')
    compose_flags = ('-f docker-compose-{}.yml -f tests/docker-compose.yml up -d'.format(compose_suffix)).split(' ')
    if config.getoption('--single-node'):
        compose_flags.append('elasticsearch1')

    run(['docker-compose'] + compose_flags)


def pytest_unconfigure(config):
    run(['docker-compose', '-f', 'docker-compose-{}.yml'.format(config.getoption('--image-flavor')), 'down', '-v'])
    run(['docker-compose', '-f', 'docker-compose-{}.yml'.format(config.getoption('--image-flavor')), 'rm', '-f', '-v'])
