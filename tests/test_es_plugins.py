from .fixtures import elasticsearch
import pytest
from requests import codes


def test_IngestUserAgentPlugin_is_installed(elasticsearch):
    # Ensure IngestUserAgentPlugin is present on all nodes
    for nodeplugins in elasticsearch.get_node_plugins():
        plugin_classnames = [plugin['classname'] for plugin in nodeplugins]
        assert 'org.elasticsearch.ingest.useragent.IngestUserAgentPlugin' in plugin_classnames


def test_IngestGeoIpPlugin_is_installed(elasticsearch):
    # Ensure IngestGeoIpPlugin is present on all nodes
    for nodeplugins in elasticsearch.get_node_plugins():
        plugin_classnames = [plugin['classname'] for plugin in nodeplugins]
        assert 'org.elasticsearch.ingest.geoip.IngestGeoIpPlugin' in plugin_classnames
