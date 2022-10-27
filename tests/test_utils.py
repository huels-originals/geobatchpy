import os

import pytest

from geobatchpy.utils import get_api_url, get_api_key, API_PLACES


def test_get_api_url():
    url = get_api_url(api=API_PLACES, api_key='123', version=52)
    assert url == 'https://api.geoapify.com/v52/places?apiKey=123'

    os.environ['GEOAPIFY_KEY'] = '456'

    url = get_api_url(api=API_PLACES)
    assert url == 'https://api.geoapify.com/v2/places?apiKey=456'


def test_get_api_key():
    assert '456' == get_api_key(api_key='456')

    with pytest.raises(KeyError):
        get_api_key(env_variable_name='_NOT_EXISTING_VAR')

    os.environ['SOME_API_VAR'] = '123'
    assert '123' == get_api_key(env_variable_name='SOME_API_VAR')
