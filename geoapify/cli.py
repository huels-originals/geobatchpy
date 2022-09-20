import logging
import os
from datetime import datetime
from uuid import uuid4

import click

from geoapify import Client
from geoapify.batch import read_data_from_json_file, write_data_to_json_file

logging.basicConfig(level=logging.DEBUG)

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}


def get_api_key(api_key: str = None) -> str:
    if api_key is None:
        try:
            api_key = os.environ['GEOAPIFY_KEY']
        except KeyError:
            logging.error('Set the --key option or set the key in the \'GEOAPIFY_KEY\' environment variable.')
            raise
    return api_key


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    CLI for the Geoapify REST API.

    Set your GEOAPIFY_KEY environment variable or provide the key using the --api-key option.

    \b
    geoapify post_batch_jobs <path-data-in> <path-data-out> [-k <api-key>]  -> Post batch jobs and store result urls.
    geoapify monitor_batch_jobs <path-data-in> <path-data-out> [-k <api-key>]  -> Monitor jobs and store results.
    """
    pass


@main.command()
@click.argument('path_data_in', type=click.Path(exists=True))
@click.argument('path_data_out', type=click.Path())
@click.option('-k', '--api-key', default=None)
def post_batch_jobs(path_data_in, path_data_out, api_key):
    """Read input data, post batch jobs, and write result urls to disk.

    Specifications of file `path_data_in` - JSON dictionary with the following attributes:
    Mandatory:
    - api: string, the name of the Geoapify API. E.g., '/v1/geocode/search'.
    - inputs: list of locations in any of the supported formats. See geoapify.batch.BatchClient.
    - params: dict of optional parameters valid for all locations. See the Geoapify API docs.
    Optional:
    - batch_len: int, maximal size of a single batch. Data will be distributed across multiple jobs if needed.
    - id: str, any name for reference. This will be stored as the data_input_id in the outputs.

    :param path_data_in: path to the JSON file read as input.
    :param path_data_out: destination of the JSON output file.
    :param api_key: if not set, will be read from the GEOAPIFY_KEY environment variable.
    """
    data_in = read_data_from_json_file(file_path=path_data_in)
    client = Client(api_key=get_api_key(api_key=api_key))
    result_urls = client.batch.post_batch_jobs_and_get_job_urls(
        api=data_in['api'], inputs=data_in['inputs'], parameters=data_in['params'], batch_len=data_in.get('batch_len'))

    data_out = {
        'id': str(uuid4()),
        'api': data_in['api'],
        'result_urls': result_urls,
        'sleep_time': client.batch.get_sleep_time(number_of_items=len(data_in['inputs'])),
        'data_input_id': data_in.get('id'),
        'dt_created': str(datetime.now())
    }
    write_data_to_json_file(data=data_out, file_path=path_data_out)


@main.command()
@click.argument('path_data_in', type=click.Path(exists=True))
@click.argument('path_data_out', type=click.Path())
@click.option('-k', '--api-key', default=None)
def monitor_batch_jobs(path_data_in, path_data_out, api_key):
    """Read result urls from input data, monitor batch jobs, and write results to disk.

    Specifications of file `path_data_in` - JSON dictionary with the following attributes:
    Mandatory:
    - result_urls: list of URLs referencing the batch jobs running on the Geoapify servers.
    - sleep_time: int, sleep time in seconds between every GET call of a single job to check the status.
    Optional:
    - id: str, any name for reference. This will be stored as the data_input_id in the outputs.

    :param path_data_in: path to the JSON file read as input.
    :param path_data_out: destination of the JSON output file.
    :param api_key: if not set, will be read from the GEOAPIFY_KEY environment variable.
    """
    data_in = read_data_from_json_file(file_path=path_data_in)
    client = Client(api_key=get_api_key(api_key=api_key))
    results = client.batch.monitor_batch_jobs_and_get_results(
        result_urls=data_in['result_urls'], sleep_time=data_in['sleep_time'])

    data_out = {
        'id': str(uuid4()),
        'results': results,
        'data_input_id': data_in.get('id'),
        'dt_created': str(datetime.now())
    }
    write_data_to_json_file(data=data_out, file_path=path_data_out)


if __name__ == '__main__':
    main()
