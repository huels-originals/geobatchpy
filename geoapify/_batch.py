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
from typing import List, Any, Union
from pathlib import Path

import requests

HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}
logger = logging.getLogger(__name__)


def request_batch_processing_and_get_urls(
        request_url: str, inputs: List[Any] = None, inputs_file_path: Union[str, Path] = None,
        parameters: dict = None, batch_len: int = 1000, write_urls_to: Union[str, Path] = None) -> List[str]:
    """Triggers batch process on server and returns URLs to be used in GET requests for obtaining results.

    The returned URLs represent a batch each. There is a limit in batch size of 1000 which usually means we need
    to split our workload into multiple batches. But even if the size of our inputs is smaller than 1000, it can
    help to further limit the size of batches. Several smaller batches may be processed quicker than a few large ones.
    """
    if inputs is not None:
        pass
    elif inputs_file_path is not None:
        inputs = read_inputs_from_file(file_path=inputs_file_path)
    else:
        raise ValueError('\'inputs\' abd \'inputs_file_path\' cannot be both None.')

    batch_len = max(min(batch_len, 1000), 2)  # limit of 1000 dictated by API

    batches = []
    for i in range(math.ceil(len(inputs) / batch_len)):
        batches.append(inputs[i * batch_len:(i + 1) * batch_len])

    result_urls = []
    for batch in batches:
        url = requests.post(request_url, json=batch, headers=HEADERS, params=parameters).json()['url']
        result_urls.append(url)
        time.sleep(0.1)

    if write_urls_to is not None:
        header = f'Endpoint={request_url}, Datetime={datetime.now()}'
        write_urls_to_file(urls=result_urls, file_path=write_urls_to, header=header)

    return result_urls


def wait_for_batches_to_complete(result_urls: List[str] = None, result_urls_file_path: Union[str, Path] = None,
                                 sleep_time: int = 5) -> List[dict]:
    """Waits for the completion of all batch processing requests and returns results as a list of dictionaries.

    A previous POST request responded with `get_url` and geocoding computation has been triggered. A GET request
    using `get_url` as the argument will contain the geocoding results only after computation is finished.
    Otherwise the response will be rather empty.
    """
    if result_urls is not None:
        pass
    elif result_urls_file_path is not None:
        result_urls = read_urls_from_file(file_path=result_urls_file_path)
    else:
        raise ValueError('\'result_urls\' and \'result_urls_path\' cannot be both None.')

    result_responses = []
    for url in result_urls:
        while True:
            get_response = requests.get(url, headers=HEADERS).json()
            try:
                _ = get_response[0]['query']
                break
            except KeyError:
                time.sleep(max(sleep_time, 2))
        result_responses += get_response
    return result_responses


def write_urls_to_file(urls: List[str], file_path: Union[str, Path], header: str = None) -> None:
    file_path = Path(file_path)
    with open(file_path, 'w') as f:
        if header is not None and not header.startswith('https'):
            f.write(f'{header}\n')
        elif header is not None and header.startswith('https'):
            raise ValueError('Headers starting with \'https\' are forbidden.')
        for url in urls:
            f.write(f'{url}\n')


def read_inputs_from_file(file_path: Union[str, Path]) -> List[Any]:
    pass


def read_urls_from_file(file_path: Union[str, Path]) -> List[str]:
    urls = []
    with open(Path(file_path), 'r') as f:
        for row in f:
            if row.startswith('https'):
                urls.append(row.replace('\n', ''))
    return urls
