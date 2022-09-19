"""Batch processing utility functions.

geoapify.com offers several of its services in a batch version. They all work the same: you start with a list of
records and ask to process each component. Processing is component-wise independent and can be POSTed in a batch
instead requesting for each component separately. Geoapify is able to distribute processing on its servers. You can
use GET requests to ask if a job is completed. If it is, you can GET the results for a complete batch.
"""
import logging
import math
from datetime import datetime
import time
from typing import List, Any, Union, Dict, Tuple
from pathlib import Path
import json

import requests

HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}


class BatchClient:

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._logger = logging.getLogger(__name__)

    def geocode(self, addresses: List[str], batch_len: int = 1000, parameters: Dict[str, str] = None,
                simplify_output: bool = False) -> List[dict]:
        inputs = [{'params': {'text': val}} for val in addresses]
        result_urls = self.post_batch_jobs_and_get_job_urls(
            api='/v1/geocode/search', inputs=inputs, parameters=parameters, batch_len=batch_len)

        results = self.monitor_batch_jobs_and_get_results(result_urls=result_urls)

        if simplify_output:
            return [{**res['result']['results'][0], 'query': res['result']['query']} for res in results]
        else:
            return results

    def reverse_geocode(self, geocodes: List[Tuple[float, float]], batch_len: int = 1000,
                        parameters: Dict[str, str] = None, simplify_output: bool = False) -> List[dict]:
        inputs = [{'params': {'lat': val[1], 'lon': val[0]}} for val in geocodes]
        result_urls = self.post_batch_jobs_and_get_job_urls(
            api='/v1/geocode/reverse', inputs=inputs, parameters=parameters, batch_len=batch_len)

        results = self.monitor_batch_jobs_and_get_results(result_urls=result_urls)

        if simplify_output:
            return [res['result']['results'][0] for res in results]
        else:
            return results

    def place_details(self, place_ids: List[str] = None, geocodes: List[Tuple[float, float]] = None,
                      batch_len: int = 1000, parameters: Dict[str, str] = None,
                      features: List[str] = None, language: str = None) -> List[dict]:
        if place_ids is not None:
            inputs = [{'params': {'id': val}} for val in place_ids]
        elif geocodes is not None:
            inputs = [{'params': {'lat': val[1], 'lon': val[0]}} for val in geocodes]
        else:
            raise ValueError('Either place_ids or geocodes must be provided.')

        params = dict()
        if features is not None:
            params['features'] = ','.join(features)
        if language is not None:
            params['lang'] = language

        result_urls = self.post_batch_jobs_and_get_job_urls(
            api='/v2/place-details', inputs=inputs, parameters=params, batch_len=batch_len)

        results = self.monitor_batch_jobs_and_get_results(result_urls=result_urls)

        return results

    def post_batch_jobs_and_get_job_urls(self, api: str, inputs: List[Any] = None,
                                         inputs_file_path: Union[str, Path] = None,
                                         parameters: dict = None, batch_len: int = 1000,
                                         write_urls_to: Union[str, Path] = None) -> List[str]:
        """Triggers batch process on server and returns URLs to be used in GET requests for obtaining results.

        The returned URLs represent a batch each. There is a limit in batch size of 1000 which usually means we need
        to split our workload into multiple batches. But even if the size of our inputs is smaller than 1000, it can
        help to further limit the size of batches. Several smaller batches may be processed quicker than a few large
        ones.
        """
        if inputs is not None:
            pass
        elif inputs_file_path is not None:
            inputs = self.read_list_from_json(file_path=inputs_file_path)
        else:
            raise ValueError('\'inputs\' abd \'inputs_file_path\' cannot be both None.')

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
                    'https://api.geoapify.com/v1/batch?apiKey={}'.format(self._api_key), json=data, headers=HEADERS)
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            if response.status_code not in (200, 202):
                raise ValueError(f'The service failed to create the job for batch {i}' +
                                 f' - check input range {i * batch_len}:{min((i + 1) * batch_len, len(inputs))}.')
            url = response.json()['url']
            result_urls.append(url)
            time.sleep(0.1)

        if write_urls_to is not None:
            header = f'Endpoint=TODO, Datetime={datetime.now()}'
            self.write_list_to_json(data=result_urls, file_path=write_urls_to, attribute_name='urls', meta_data=header)

        return result_urls

    def monitor_batch_jobs_and_get_results(self, result_urls: List[str] = None,
                                           result_urls_file_path: Union[str, Path] = None) -> List[dict]:
        """Monitors completion of each batch processing job and returns/stores results.

        Previous POST requests started batch processing jobs on geopify.com servers. Here we monitor the status and
        return/store results when all jobs succeeded.

        TODO: https://superfastpython.com/threadpoolexecutor-progress/
        """
        sleep_time = 5  # TODO make this dynamic and dependent on batch size
        if result_urls is not None:
            pass
        elif result_urls_file_path is not None:
            result_urls = self.read_list_from_json(file_path=result_urls_file_path, attribute_name='urls')
        else:
            raise ValueError('\'result_urls\' and \'result_urls_path\' cannot be both None.')

        result_responses = []
        for url in result_urls:
            while True:
                response = requests.get(url, headers=HEADERS).json()
                print(response)
                try:
                    _ = response['results']
                    break
                except KeyError:
                    time.sleep(sleep_time)
            result_responses += response['results']
        return result_responses

    @staticmethod
    def write_list_to_json(data: List[Any], file_path: Union[str, Path], attribute_name: str = 'data',
                           meta_data: Any = None) -> None:
        data = {
            'meta_data': meta_data,
            attribute_name: data
        }
        with open(Path(file_path), 'w') as f:
            json.dump(data, fp=f, indent=4)

    @staticmethod
    def read_list_from_json(file_path: Union[str, Path], attribute_name: str = 'data') -> List[Any]:
        with open(Path(file_path), 'r') as f:
            data = json.load(fp=f)
        return data[attribute_name]
