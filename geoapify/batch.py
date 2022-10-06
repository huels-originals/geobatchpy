"""Batch processing utility functions.

geoapify.com offers several of its services in a batch version. They all work the same: you start with a list of
records and ask to process each component. Processing is component-wise independent and can be POSTed in a batch
instead requesting for each component separately. Geoapify is able to distribute processing on its servers. You can
use GET requests to ask if a job is completed. If it is, you can GET the results for a complete batch.
"""
import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import List, Any, Dict, Tuple, Union

import requests

from geoapify.utils import get_api_url, API_BATCH, API_GEOCODE, API_PLACES, API_PLACE_DETAILS, API_REVERSE_GEOCODE


class BatchClient:

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._lock = Lock()
        self._number_completed_jobs = 0
        self._total_number_jobs = 0
        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self._logger = logging.getLogger(__name__)

    def geocode(self, locations: List[Union[str, Dict]], batch_len: int = 1000, parameters: Dict[str, str] = None,
                simplify_output: bool = False) -> List[dict]:
        """Returns batch geocoding results as a list of dictionaries.

        Note: this whole process may take long time (hours), depending on the size of the input, the number of
        batches, and the level of your geoapify.com subscription. In such a case, it may make more sense to store
        the job URLs to disk, stop there, and continue later with monitor_batch_jobs_and_get_results.

        Arguments:
            locations: locations in a supported format as validated in parse_geocoding_inputs.
            batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
            parameters: optional parameters as key value pairs that apply to all locations. See the Geoapify docs.
            simplify_output: if True, returns output in simplified format, including only top match per address.

        Returns:
            List of structured, geocoded, and enriched address records.
        """
        inputs = parse_geocoding_inputs(locations=locations)
        result_urls = self.post_batch_jobs_and_get_job_urls(
            api=API_GEOCODE, inputs=inputs, parameters=parameters, batch_len=batch_len)

        sleep_time = self.get_sleep_time(number_of_items=len(inputs))
        results = self.monitor_batch_jobs_and_get_results(sleep_time=sleep_time, result_urls=result_urls)

        if simplify_output:
            return [{**res['result']['results'][0], 'query': res['result']['query']} if 'results' in res['result'] else
                    {**res['result'], 'query': res['params']['text']}
                    for res in results]
        else:
            return results

    def reverse_geocode(self, geocodes: List[Union[Tuple[float, float], Dict[str, float]]], batch_len: int = 1000,
                        parameters: Dict[str, str] = None, simplify_output: bool = False) -> List[dict]:
        """Returns batch reverse geocoding results as a list of dictionaries.

        Note: this whole process may take long time (hours), depending on the size of the input, the number of
        batches, and the level of your geoapify.com subscription. In such a case, it may make more sense to store
        the job URLs to disk, stop there, and continue later with monitor_batch_jobs_and_get_results.

        Arguments:
            geocodes: list of geocodes as supported by self.parse_geocodes.
            batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
            parameters: optional parameters as dictionary. See the geoapify.com API documentation.
            simplify_output: if True, the output will be provided in a slightly simplified format.

        Returns:
            List of structured, reverse geocoded, and enriched address records.
        """
        inputs = parse_geocodes(geocodes=geocodes)
        result_urls = self.post_batch_jobs_and_get_job_urls(
            api=API_REVERSE_GEOCODE, inputs=inputs, parameters=parameters, batch_len=batch_len)

        sleep_time = self.get_sleep_time(number_of_items=len(inputs))
        results = self.monitor_batch_jobs_and_get_results(sleep_time=sleep_time, result_urls=result_urls)

        if simplify_output:
            return [res['result']['results'][0] for res in results]
        else:
            return results

    def places(self, individual_parameters: List[dict], parameters: dict = None, batch_len: int = 1000) -> List[dict]:
        """Returns batch places results as a list of dictionaries.

        Every Places call is defined by a set of parameters. See the Geoapify API docs to get an overview. In the
        batch version, we can provide those parameters in two arguments. `individual_parameters` is a list of
        dictionaries, one per call, which defines parameters applicable to individual calls. The `parameters` dictionary
        applies to all calls of the batch.

        Arguments:
            individual_parameters: one dictionary per Places call.
            parameters: one dictionary with common parameters for all calls.
            batch_len: split calls into chunks of maximal size batch_len for parallel processing.

        Returns:
            List of structured Places responses.
        """
        inputs = [{'params': params} for params in individual_parameters]
        result_urls = self.post_batch_jobs_and_get_job_urls(
            api=API_PLACES, inputs=inputs, parameters=parameters, batch_len=batch_len)

        sleep_time = self.get_sleep_time(number_of_items=len(inputs))
        results = self.monitor_batch_jobs_and_get_results(sleep_time=sleep_time, result_urls=result_urls)

        return results

    def place_details(self, place_ids: List[str] = None,
                      geocodes: List[Union[Tuple[float, float], Dict[str, float]]] = None,
                      batch_len: int = 1000, features: List[str] = None, language: str = None) -> List[dict]:
        """Returns batch place details results as a list of dictionaries.

        Note: this whole process may take long time (hours), depending on the size of the input, the number of
        batches, and the level of your geoapify.com subscription. In such a case, it may make more sense to store
        the job URLs to disk, stop there, and continue later with monitor_batch_jobs_and_get_results.

        Use either place_ids or geocodes to encode your inputs. place_ids is prioritized if both are not None.

        See the Geoapify.com API docs for a list of available features.

        Arguments:
            place_ids: list of place_id values.
            geocodes: list of geocodes as supported by self.parse_geocodes.
            batch_len: split addresses into chunks of maximal size batch_len for parallel processing.
            features: list of types of details. Defaults to just ["details"] if not specified.
            language: 2-character iso language code.

        Returns:
            List of structured, reverse geocoded, and enriched address records.
        """
        if place_ids is not None:
            inputs = [{'params': {'id': val}} for val in place_ids]
        elif geocodes is not None:
            inputs = parse_geocodes(geocodes=geocodes)
        else:
            raise ValueError('Either place_ids or geocodes must be provided.')

        params = dict()
        if features is not None:
            params['features'] = ','.join(features)
        if language is not None:
            params['lang'] = language

        result_urls = self.post_batch_jobs_and_get_job_urls(
            api=API_PLACE_DETAILS, inputs=inputs, parameters=params, batch_len=batch_len)

        sleep_time = self.get_sleep_time(number_of_items=len(inputs))
        results = self.monitor_batch_jobs_and_get_results(sleep_time=sleep_time, result_urls=result_urls)

        return results

    def post_batch_jobs_and_get_job_urls(self, api: str, inputs: List[Any],
                                         parameters: dict = None, batch_len: int = None) -> List[str]:
        """Triggers batch process on server and returns URLs to be used in GET requests for obtaining results.

        The returned URLs represent a batch each. There is a limit in batch size of 1000 which usually means we need
        to split our workload into multiple batches. But even if the size of our inputs is smaller than 1000, it can
        help to further limit the size of batches. Several smaller batches may be processed quicker than a few large
        ones.

        Available api values:
        - geocoding: '/v1/geocode/search'
        - reverse geocoding: '/v1/geocode/reverse'
        - place details: '/v2/place-details'

        Arguments:
            api: name of the batch enabled API - see above.
            inputs: list of locations to be processed by batch jobs.
            parameters: optional parameters - see the Geoapify API docs.
            batch_len: maximal size of a single batch - between 2 and 1000.

        Returns:
            List of batch job URLs.
        """
        if batch_len is None:
            batch_len = 1000
        else:
            batch_len = max(min(batch_len, 1000), 2)  # limit of 1000 dictated by API

        batches = []
        for i in range(math.ceil(len(inputs) / batch_len)):
            batches.append(inputs[i * batch_len:(i + 1) * batch_len])

        result_urls = []
        for i, batch in enumerate(batches):
            params = {'format': 'json'}
            if parameters is not None:
                params = {**params, **parameters}
            data = {
                'api': api,
                'params': params,
                'inputs': batch
            }
            try:
                response = requests.post(
                    get_api_url(api=API_BATCH, api_key=self._api_key), json=data, headers=self._headers)
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            if response.status_code == 401:
                raise ValueError(response.content)
            elif response.status_code not in (200, 202):
                raise ValueError(f'Service responded with {response.content} - failed to create the job for batch {i}' +
                                 f' - check input range {i * batch_len}:{min((i + 1) * batch_len, len(inputs))}.')
            url = response.json()['url']
            result_urls.append(url)
            time.sleep(0.1)

        return result_urls

    def monitor_batch_jobs_and_get_results(self, sleep_time: int, result_urls: List[str]) -> List[dict]:
        """Monitors completion of each batch processing job and returns/stores results.

        Previous POST requests started batch processing jobs on geopify.com servers. Here we monitor the status and
        return/store results when all jobs succeeded.

        Arguments:
            sleep_time: time in seconds to sleep between every request for a single job.
            result_urls: list of batch job URLs that are to be monitored.

        Returns:
            Batch job results as a list - one element per location.
        """
        self._total_number_jobs = len(result_urls)
        sleep_time = max(sleep_time, 3)

        with ThreadPoolExecutor(min(10, len(result_urls))) as executor:
            results = executor.map(lambda x: self._task(url=x, sleep_time=sleep_time), result_urls)

        result_responses = []
        for result in results:
            result_responses += result

        return result_responses

    def _task(self, url: str, sleep_time: int) -> List[dict]:
        job_id = url.split('&apiKey')[0]
        while True:
            response = requests.get(url, headers=self._headers).json()
            print(response)
            try:
                _ = response['results']
                with self._lock:
                    self._number_completed_jobs += 1
                    self._logger.info(
                        f'Job {job_id} done - {self._number_completed_jobs}/{self._total_number_jobs} completed.')
                break
            except KeyError:
                if response['status'] == 'pending':
                    self._logger.info(f'Job {job_id} still pending - waiting another {sleep_time} seconds.')
                else:
                    self._logger.warning(
                        f'Unexpected response from server: {response} - waiting another {sleep_time} seconds.')
                time.sleep(sleep_time)
        return response['results']

    @staticmethod
    def get_sleep_time(number_of_items: int) -> int:
        """Choose an appropriate sleep time between GET requests for a batch job.

        Arguments:
            number_of_items: original number of items/addresses/locations/etc.

        Returns:
            Sleep time in seconds.
        """
        return min(300, max(3, int(number_of_items ** 0.4)))


def parse_geocoding_inputs(locations: List[Union[str, dict]]) -> List[dict]:
    """Validate and parse the input for the batch geocoding API.

    Supported formats:
    - List of free text search strings.
    - List of dictionaries with structured location definition. See the Geoapify API docs for forward geocoding.

    Arguments:
        locations: original input.

    Returns:
        Parsed locations.
    """
    if all(isinstance(val, str) for val in locations):
        # Then this is a list of free text search strings:
        return [{'params': {'text': val}} for val in locations]
    elif all(isinstance(val, dict) for val in locations):
        # Then it must be a structured input - see the Geoapify API docs.
        return [{'params': dictionary} for dictionary in locations]
    else:
        raise ValueError('Format of \'locations\' not supported.')


def parse_geocodes(geocodes: List[Union[Tuple[float, float], Dict[str, float]]]) -> List[dict]:
    """Validate and parse lists of geocoordinates.

    Supported formats:
    - List of (longitude, latitude) tuples as floats.
    - List of dictionaries, with each containing attributes 'lon' and 'lat'.

    Arguments:
        geocodes: original input.

    Returns:
        parsed geocodes.
    """
    if all(len(val) == 2 and isinstance(val[0], float) and isinstance(val[1], float) for val in geocodes):
        # Interpreted as (longitude, latitude) tuples:
        return [{'params': {'lon': val[0], 'lat': val[1]}} for val in geocodes]
    elif all(isinstance(val, dict) for val in geocodes):
        return [{'params': val} for val in geocodes]
    else:
        raise ValueError('Format of \'geocodes\' not supported.')
