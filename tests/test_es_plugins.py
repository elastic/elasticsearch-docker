from .fixtures import elasticsearch
from requests import codes


def test_uninstall_xpack_plugin(elasticsearch):
    # Ensure plugins can be uninstalled, see https://github.com/elastic/elasticsearch/issues/24231
    assert elasticsearch.uninstall_plugin("x-pack").exit_status == 0
