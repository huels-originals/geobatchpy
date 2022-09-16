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
    _url_batch_geocode = 'https://api.geoapify.com/v1/batch/geocode/search?apiKey={}'
    _url_batch_reverse_geocode = 'https://api.geoapify.com/v1/batch/geocode/reverse?&apiKey={}'

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._logger = logging.getLogger(__name__)

    def geocode(self, addresses: List[str], batch_len: int = 1000, sleep_time: int = 5,
                parameters: Dict[str, str] = None):
        result_urls = self.post_batch_jobs_and_get_job_urls(
            request_url=self._url_batch_geocode.format(self._api_key), inputs=addresses, batch_len=batch_len,
            parameters=parameters)

        return self.monitor_batch_jobs_and_get_results(result_urls=result_urls, sleep_time=sleep_time)

    def reverse_geocode(self, geocodes: List[Tuple[float, float]], batch_len: int = 1000, sleep_time: int = 5,
                        parameters: Dict[str, str] = None):
        result_urls = self.post_batch_jobs_and_get_job_urls(
            request_url=self._url_batch_reverse_geocode.format(self._api_key), inputs=geocodes, batch_len=batch_len,
            parameters=parameters)

        return self.monitor_batch_jobs_and_get_results(result_urls=result_urls, sleep_time=sleep_time)

    def post_batch_jobs_and_get_job_urls(
            self, request_url: str, inputs: List[Any] = None, inputs_file_path: Union[str, Path] = None,
            parameters: dict = None, batch_len: int = 1000, write_urls_to: Union[str, Path] = None) -> List[str]:
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
            try:
                response = requests.post(request_url, json=batch, headers=HEADERS, params=parameters)
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            if response.status_code not in (200, 202):
                raise ValueError(f'The service failed to create the job for batch {i}' +
                                 f' - check input range {i * batch_len}:{min((i + 1) * batch_len, len(inputs))}.')
            url = response.json()['url']
            result_urls.append(url)
            time.sleep(0.1)

        if write_urls_to is not None:
            header = f'Endpoint={request_url}, Datetime={datetime.now()}'
            self.write_list_to_json(data=result_urls, file_path=write_urls_to, attribute_name='urls', meta_data=header)

        return result_urls

    def monitor_batch_jobs_and_get_results(self, result_urls: List[str] = None,
                                           result_urls_file_path: Union[str, Path] = None,
                                           sleep_time: int = 5) -> List[dict]:
        """Monitors completion of each batch processing job and returns/stores results.

        Previous POST requests started batch processing jobs on geopify.com servers. Here we monitor the status and
        return/store results when all jobs succeeded.
        """
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
                try:
                    _ = response[0]['query']
                    break
                except KeyError:
                    time.sleep(max(sleep_time, 2))
            result_responses += response
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
