from .fixtures import elasticsearch
from requests import codes
import pytest

image_flavor = pytest.config.getoption('--image-flavor')


def test_presence_of_xpack(elasticsearch):
    response = elasticsearch.get('/_xpack')
    if image_flavor == 'oss':
        assert response.status_code == codes.bad_request
    else:
        assert response.status_code == codes.ok
