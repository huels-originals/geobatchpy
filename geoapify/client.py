import logging
from typing import Dict, List, Tuple

import requests

from geoapify._batch import request_batch_processing_and_get_urls, wait_for_batches_to_complete, HEADERS


class Client:
    def __init__(self, api_key: str):
        self._api_key = api_key

        self._logger = logging.getLogger(__name__)

    def place_details(self, place_id: str = None, longitude: float = None, latitude: float = None,
                      features: List[str] = None, language: str = None):
        """Returns place details of a location.

        Use either the `place_id` (returned by geocoding) or geo coordinates to specify a location. The `features`
        argument specifies which kind of details to request. See the geoapify.com documentation.

        :param place_id: the Nominatim place_id as a string.
        :param latitude: float or string representing latitude.
        :param longitude: float or string representing longitude.
        :param features: list of types of details. Defaults to just ["details"] if not specified.
        :param language: 2-character iso language code.
        :return: dictionary of location details.
        """
        request_url = 'https://api.geoapify.com/v2/place-details?apiKey={}'.format(self._api_key)
        params = dict()
        if place_id is not None:
            params['id'] = place_id
        elif latitude is not None and longitude is not None:
            params['lat'] = str(latitude)
            params['lon'] = str(longitude)
        else:
            raise ValueError('Either place_id or latitude and longitude must be provided.')
        if features is not None:
            params['features'] = ','.join(features)
        if language is not None:
            params['lang'] = language

        return requests.get(url=request_url, params=params, headers=HEADERS).json()

    def geocode(self, text: str = None, parameters: Dict[str, str] = None) -> dict:
        """Returns geocoding results as a dictionary.

        Use either a free text search wit the `text` argument or alternatively provide input in a structured
        form using the `parameters` argument. See the geoapify.com documentation.

        :param text: free text search of a location.
        :param parameters: structured search as key value pairs in a dictionary.
        :return: geocoding results as a dictionary.
        """
        request_url = 'https://api.geoapify.com/v1/geocode/search?apiKey={}'.format(self._api_key)

        params = {'text': text} if text is not None else dict()
        if parameters is not None:
            params = {**params, **parameters}

        return requests.get(url=request_url, params=params, headers=HEADERS).json()

    def reverse_geocode(self, longitude: float, latitude: float) -> dict:
        """Returns reverse geocoding results as a dictionary.

        :param latitude: float or string representing latitude.
        :param longitude: float or string representing longitude.
        :return: result as a dictionary.
        """
        request_url = 'https://api.geoapify.com/v1/geocode/reverse?apiKey={}'.format(self._api_key)
        params = {'lat': str(latitude), 'lon': str(longitude)}

        return requests.get(url=request_url, params=params, headers=HEADERS).json()

    def batch_geocode(self, addresses: List[str], batch_len: int = 1000, sleep_time: int = 5,
                      parameters: Dict[str, str] = None) -> List[dict]:
        """Returns batch geocoding results as a list of dictionaries.

        :param addresses: search queries as list of strings; one address = one string.
        :param sleep_time: sleep time in seconds between every request for results of batch processing.
        :param batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
        :param parameters: optional parameters as key value paris. See the geoapify documentation.
        """
        request_url = 'https://api.geoapify.com/v1/batch/geocode/search?apiKey={}'.format(self._api_key)

        result_urls = request_batch_processing_and_get_urls(
            request_url=request_url, inputs=addresses, batch_len=batch_len, parameters=parameters)

        return wait_for_batches_to_complete(result_urls=result_urls, sleep_time=sleep_time)

    def batch_reverse_geocode(self, geocodes: List[Tuple[float, float]], batch_len: int = 1000, sleep_time: int = 5,
                              parameters: Dict[str, str] = None) -> List[dict]:
        """Returns batch reverse geocoding results as a list of dictionaries.

        :param geocodes: list of longitude, latitude tuples.
        :param batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
        :param sleep_time: sleep time in seconds between every request for results of batch processing.
        :param parameters: optional parameters as dictionary. See geoapify.com documentation.
        """
        request_url = 'https://api.geoapify.com/v1/batch/geocode/reverse?&apiKey={}'.format(self._api_key)

        result_urls = request_batch_processing_and_get_urls(
            request_url=request_url, inputs=geocodes, batch_len=batch_len, parameters=parameters)

        return wait_for_batches_to_complete(result_urls=result_urls, sleep_time=sleep_time)
