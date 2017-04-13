from subprocess import run
import pytest


def pytest_addoption(parser):
    """By default run tests in clustered mode, but allow dev mode with --single-node"""
    parser.addoption('--single-node', action='store_true',
                     help='non-clustered version')


def pytest_configure(config):
    compose_flags = '-f docker-compose.yml -f docker-compose.hostports.yml up -d'.split(' ')
    if config.getoption('--single-node'):
        compose_flags.append('elasticsearch1')

    run(['docker-compose'] + compose_flags)


def pytest_unconfigure(config):
    run(['docker-compose', 'down', '-v'])
    run(['docker-compose', 'rm', '-f', '-v'])
