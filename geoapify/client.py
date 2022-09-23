import logging
import warnings
from typing import Dict, List, Tuple, Union

import requests

from geoapify.batch import BatchClient
from geoapify.utils import get_api_url, API_GEOCODE, API_REVERSE_GEOCODE, API_PLACES, API_PLACE_DETAILS


class Client:

    def __init__(self, api_key: str):
        self._api_key = api_key
        self.batch = BatchClient(api_key=api_key)
        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self._logger = logging.getLogger(__name__)

    def places(self, categories: Union[str, List[str]], filter_by_region: str = None,
               filter_by_name: str = None, proximity_by: Tuple[float, float] = None,
               conditions: Union[str, List[str]] = None, limit: int = 20, offset: int = None, language: str = None):
        """Query locations of different categories.

        See the Geoapify API documentation for a full list of categories and any other supported parameters.

        :param categories: returned places must be in one of the chosen categories.
        :param filter_by_region: places must be within boundaries of the specified geometry.
        :param filter_by_name: places' names are used for filtering.
        :param proximity_by: (lon, lat) tuple; places will be returned in order of proximity to the coordinates.
        :param conditions: places must fulfill all of the provided conditions.
        :param limit: maximal number of places returned.
        :param offset: return next places by starting counting from `offset`.
        :param language: iso code of the language in which places should be returned.
        :return: list of places encoded in JSON like dictionaries.
        """
        request_url = get_api_url(api=API_PLACES, api_key=self._api_key)
        params = dict()
        if isinstance(categories, str):
            params['categories'] = categories
        else:
            params['categories'] = ','.join(categories)
        if filter_by_region is not None:
            params['filter'] = filter_by_region
        if filter_by_name is not None:
            params['name'] = filter_by_name
        if proximity_by is not None:
            params['bias'] = f'proximity:{proximity_by[0]},{proximity_by[1]}'
        if isinstance(conditions, str):
            params['conditions'] = conditions
        elif conditions is not None:
            params['conditions'] = ','.join(conditions)

        params['limit'] = limit
        params['offset'] = offset
        if language is not None:
            params['lang'] = language

        return requests.get(url=request_url, params=params, headers=self._headers).json()

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
        :return: structured location details.
        """
        request_url = get_api_url(api=API_PLACE_DETAILS, api_key=self._api_key)
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

        return requests.get(url=request_url, params=params, headers=self._headers).json()

    def geocode(self, text: str = None, parameters: Dict[str, str] = None) -> dict:
        """Returns geocoding results as a dictionary.

        Use either a free text search wit the `text` argument or alternatively provide input in a structured
        form using the `parameters` argument. See the geoapify.com API documentation.

        :param text: free text search of a location.
        :param parameters: structured search as key value pairs and other optional parameters.
        :return: structured, geocoded, and enriched address records.
        """
        request_url = get_api_url(api=API_GEOCODE, api_key=self._api_key)

        params = {'text': text} if text is not None else dict()
        if parameters is not None:
            params = {**params, **parameters}

        return requests.get(url=request_url, params=params, headers=self._headers).json()

    def reverse_geocode(self, longitude: float, latitude: float) -> dict:
        """Returns reverse geocoding results as a dictionary.

        :param latitude: float or string representing latitude.
        :param longitude: float or string representing longitude.
        :return: structured, reverse geocoded, and enriched address records.
        """
        request_url = get_api_url(api=API_REVERSE_GEOCODE, api_key=self._api_key)
        params = {'lat': str(latitude), 'lon': str(longitude)}

        return requests.get(url=request_url, params=params, headers=self._headers).json()

    def batch_geocode(self, addresses: List[str], batch_len: int = 1000,
                      parameters: Dict[str, str] = None) -> List[dict]:
        """Returns batch geocoding results as a list of dictionaries.

        Warning: this whole process may take long time (hours), depending on the size of the input, the number of
        batches, and the level of your geoapify.com subscription.

        :param addresses: search queries as list of strings; one address = one string.
        :param batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
        :param parameters: optional parameters as key value paris. See the geoapify.com API documentation.
        :return: list of structured, geocoded, and enriched address records.
        """
        warnings.warn('Method Client.batch_geocode is deprecated - use Client.batch.geocode instead.')
        return self.batch.geocode(locations=addresses, batch_len=batch_len, parameters=parameters,
                                  simplify_output=True)

    def batch_reverse_geocode(self, geocodes: List[Tuple[float, float]], batch_len: int = 1000,
                              parameters: Dict[str, str] = None) -> List[dict]:
        """Returns batch reverse geocoding results as a list of dictionaries.

        Warning: this whole process may take long time (hours), depending on the size of the input, the number of
        batches, and the level of your geoapify.com subscription.

        :param geocodes: list of longitude, latitude tuples.
        :param batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
        :param parameters: optional parameters as dictionary. See the geoapify.com API documentation.
        :return: list of structured, reverse geocoded, and enriched address records.
        """
        warnings.warn('Method Client.batch_reverse_geocode is deprecated - use Client.batch.reverse_geocode instead.')
        return self.batch.reverse_geocode(geocodes=geocodes, batch_len=batch_len, parameters=parameters,
                                          simplify_output=True)
