import json
import logging
from pathlib import Path
from typing import Union, Dict, Any, List


API_GEOCODE = '/v1/geocode/search'
API_REVERSE_GEOCODE = '/v1/geocode/reverse'
API_PLACE_DETAILS = '/v2/place-details'
API_PLACES = '/v2/places'
API_BATCH = '/v1/batch'

Json = Union[Dict[str, Any], List[Any]]  # A superset of the JSON specification, excluding atomic objects


def get_api_url(api: str, api_key: str, version: int = None) -> str:
    url = f'https://api.geoapify.com{api}?apiKey={api_key}'
    if version is None:
        # Use version as defined above
        return url
    else:
        return url.replace('/v2/', f'/v{version}/')


def read_data_from_json_file(file_path: Union[str, Path]) -> Json:
    """Reads data from a JSON file.

    Json = Union[Dict[str, Any], List[Any]] is a superset of the JSON specification, excluding scalar objects.

    Arguments:
        file_path: path to the JSON file.

    Returns:
        The Python equivalent of the JSON object.
    """
    with open(Path(file_path), 'r') as f:
        data = json.load(fp=f)
    logging.info(f'File \'{file_path}\' read from disk.')
    return data


def write_data_to_json_file(data: Json, file_path: Union[str, Path]) -> None:
    """Writes data to a JSON file.

    Json = Union[Dict[str, Any], List[Any]] is a superset of the JSON specification, excluding scalar objects.

    Arguments:
        data: an object of Json type.
        file_path: destination path of the JSON file.
    """
    with open(Path(file_path), 'w') as f:
        json.dump(data, fp=f, indent=4)
    logging.info(f'File \'{file_path}\' written to disk.')
