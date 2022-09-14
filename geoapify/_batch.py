"""Batch processing utility functions.

geoapify.com offers several of its services in a batch version. They all work the same: you start with a list of
records and ask to process each component. Processing is component-wise independent and can be POSTed in a batch
instead requesting for each component separately. Geoapify is able to distribute processing on its servers. You can
use GET requests to ask if a job is completed. If it is, you can GET the results for a complete batch.
"""
import math
import time
from typing import List, Any

import requests

HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}


def request_batch_processing_and_get_urls(
        request_url: str, inputs: List[Any], batch_len: int, parameters: dict = None) -> List[str]:
    """Triggers batch process on server and returns URLs to be used in GET requests for obtaining results.

    The returned URLs represent a batch each. There is a limit in batch size of 1000 which usually means we need
    to split our workload into multiple batches. But even if the size of our inputs is smaller than 1000, it can
    help to further limit the size of batches. Several smaller batches may be processed quicker than a few large ones.
    """
    batch_len = max(min(batch_len, 1000), 2)  # limit of 1000 dictated by API

    batches = []
    for i in range(math.ceil(len(inputs) / batch_len)):
        batches.append(inputs[i * batch_len:(i + 1) * batch_len])

    result_urls = []
    for batch in batches:
        url = requests.post(request_url, json=batch, headers=HEADERS, params=parameters).json()['url']
        result_urls.append(url)
        time.sleep(0.5)

    return result_urls


def wait_for_batches_to_complete(result_urls: List[str], sleep_time: int) -> List[dict]:
    """Waits for the completion of all batch processing requests and returns results as a list of dictionaries.

    A previous POST request responded with `get_url` and geocoding computation has been triggered. A GET request
    using `get_url` as the argument will contain the geocoding results only after computation is finished.
    Otherwise the response will be rather empty.
    """
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
