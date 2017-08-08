from subprocess import run
import pytest


def pytest_addoption(parser):
    """Customize testinfra with config options via cli args"""

    # By default run tests in clustered mode, but allow dev mode with --single-node"""
    parser.addoption('--single-node', action='store_true',
                     help='non-clustered version')

    # Let us specify which docker-compose-(image_flavor).yml file to use
    parser.addoption('--image-flavor', action='store',
                     help='Docker image flavor; the suffix used in docker-compose-<flavor>.yml')


def pytest_configure(config):
    image_flavor = config.getoption('--image-flavor')
    compose_flags = ('-f docker-compose-{0}.yml -f tests/docker-compose-{0}.yml up -d'.format(image_flavor)).split(' ')
    if config.getoption('--single-node'):
        compose_flags.append('elasticsearch1')

    run(['docker-compose'] + compose_flags)


def pytest_unconfigure(config):
    run(['docker-compose', '-f', 'docker-compose-{}.yml'.format(config.getoption('--image-flavor')), 'down', '-v'])
    run(['docker-compose', '-f', 'docker-compose-{}.yml'.format(config.getoption('--image-flavor')), 'rm', '-f', '-v'])
