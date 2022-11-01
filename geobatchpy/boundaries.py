import logging

import requests

from geobatchpy.utils import get_api_key, get_api_url, API_BOUNDARIES_PART_OF, API_BOUNDARIES_CONSISTS_OF


class BoundariesClient:
    def __init__(self, api_key: str = None):
        self._api_key = get_api_key(api_key=api_key)
        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self._logger = logging.getLogger(__name__)

    def part_of(self, place_id: str = None, longitude: float = None, latitude: float = None,
                boundary: str = 'administrative', geometry: str = 'point', language: str = None) -> dict:
        """Returns GeoJSON of boundaries the provided location belongs to.

        Args:
            place_id: place id returned by one of the many APIs (Geometry API, Geocoding API, Places API,...).
            longitude: float representing longitude.
            latitude: float representing latitude.
            boundary: One of 'administrative' (default), 'postal_code', 'political', 'low_emission_zone'.
            geometry: One of 'point' (default), 'geometry_1000', 'geometry_5000', 'geometry_10000' for different levels
                of accuracy.
            language: 2-character iso code for the language of the result.

        Returns:
            GeoJSON of a boundary in the selected accuracy.
        """
        request_url = get_api_url(api=API_BOUNDARIES_PART_OF, api_key=self._api_key)

        params = {'boundary': boundary, 'geometry': geometry}
        if place_id is not None:
            params['id'] = place_id
        elif latitude is not None and longitude is not None:
            params['lat'] = str(latitude)
            params['lon'] = str(longitude)
        else:
            raise ValueError('Either place_id or latitude and longitude must be provided.')
        if language is not None:
            params['lang'] = language

        return requests.get(url=request_url, params=params, headers=self._headers).json()

    def consists_of(self, place_id: str, boundary: str = 'administrative', sub_level: int = 1,
                    geometry: str = 'point', language: str = None) -> dict:
        """Returns GeoJSON of boundaries that the provided location consists of.

        Args:
            place_id: place id returned by one of the many APIs (Geometry API, Geocoding API, Places API,...).
            boundary: One of 'administrative' (default), 'postal_code', 'political', 'low_emission_zone'.
            sub_level: One of 1, 2, 3, 4, 5. Relative subdivisions level as an integer.
            geometry: One of 'point' (default), 'geometry_1000', 'geometry_5000', 'geometry_10000' for different levels
                of accuracy.
            language: 2-character iso code for the language of the result.

        Returns:
            GeoJSON of boundaries the provided location consists of.
        """
        request_url = get_api_url(api=API_BOUNDARIES_CONSISTS_OF, api_key=self._api_key)

        params = {'id': place_id, 'boundary': boundary, 'sublevel': sub_level, 'geometry': geometry}
        if language is not None:
            params['lang'] = language

        return requests.get(url=request_url, params=params, headers=self._headers).json()
