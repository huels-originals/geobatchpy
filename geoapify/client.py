import logging
import math
import time

import requests


class Client:
    def __init__(self, api_key: str):
        self._api_key = api_key

        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self._logger = logging.getLogger(__name__)

    def geocode(self, text: str = None, parameters: dict[str, str] = None) -> dict:
        request_url = 'https://api.geoapify.com/v1/geocode/search?apiKey={}'.format(self._api_key)

        params = {'text': text} if text is not None else dict()
        if parameters is not None:
            params = {**params, **parameters}

        return requests.get(url=request_url, params=params, headers=self._headers).json()

    def reverse_geocode(self, latitude: str, longitude: str) -> dict:
        request_url = 'https://api.geoapify.com/v1/geocode/reverse?apiKey={}'.format(self._api_key)
        params = {'lat': latitude, 'lon': longitude}

        return requests.get(url=request_url, params=params, headers=self._headers).json()

    def batch_geocode(self, addresses: list[str], batch_len: int = 1000, sleep_time: int = 5,
                      parameters: dict[str, str] = None) -> list[dict]:
        """Returns batch geocoding results as a list of dictionaries.

        We store job URLs in a cached file. This allows to recover URLs if an unexpected error
        happens in-between posting batch processing jobs and obtaining results.

        :param addresses: search queries as list of strings; one address = one string.
        :param sleep_time: sleep time in seconds between every request for results of batch processing.
        :param batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
        :param parameters: optional parameters as key value paris. See the geoapify documentation.
        """
        request_url = 'https://api.geoapify.com/v1/batch/geocode/search?apiKey={}'.format(self._api_key)

        result_urls = self._request_batch_geocoding_and_return_result_urls(
            request_url=request_url, addresses=addresses, batch_len=batch_len, parameters=parameters)

        result_responses = []
        for url in result_urls:
            result_responses += self._get_finished_batch_processing_results(result_url=url, sleep_time=sleep_time)

        return result_responses

    def _request_batch_geocoding_and_return_result_urls(
            self, request_url: str, addresses: list[str], batch_len: int, parameters: dict = None) -> list[str]:
        """Triggers batch geocoding on server and returns URLs to be used in GET requests for obtaining results.

        """
        batch_len = min(batch_len, 1000)  # limit of 1000 dictated by API

        batches = []
        for i in range(math.ceil(len(addresses) / batch_len)):
            batches.append(addresses[i * batch_len:(i + 1) * batch_len])

        result_urls = []
        for batch in batches:
            url = requests.post(request_url, json=batch, headers=self._headers, params=parameters).json()['url']
            self._logger.info(f'Batch geocoding request posted - listen to url \'{url}\'.')
            result_urls.append(url)

        return result_urls

    def _get_finished_batch_processing_results(self, result_url: str, sleep_time: int) -> dict:
        """Waits for the completion of the geocoding batch processing request and returns the results as a response.

        A previous POST request responded with `get_url` and geocoding computation has been triggered. A GET request
        using `get_url` as the argument will contain the geocoding results only after computation is finished.
        Otherwise the response will be rather empty.
        """
        get_response = None
        pending = True
        while pending:
            get_response = requests.get(result_url, headers=self._headers).json()
            try:
                _ = get_response[0]['query']
                pending = False
                self._logger.info(f'Batch geocoding results behind url \'{result_url}\' ready.')
            except KeyError:
                time.sleep(sleep_time)
        return get_response
