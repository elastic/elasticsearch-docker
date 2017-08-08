from .fixtures import elasticsearch
import pytest
from requests import codes

image_flavor = pytest.config.getoption('--image-flavor')


@pytest.mark.skipif('oss' in image_flavor,
                    reason="x-pack not installed in the -{} image.".format(image_flavor))
def test_uninstall_xpack_plugin(elasticsearch):
    # Ensure plugins can be uninstalled, see https://github.com/elastic/elasticsearch/issues/24231
    assert elasticsearch.uninstall_plugin("x-pack").exit_status == 0


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
