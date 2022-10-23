# A CLI and Python Client for the Geoapify API

We have been using the Geoapify API to **geocode millions of location records** for data validation and analytics. We built
this package to make this process comfortable using Python and the command line.

Why Geoapify and this package may also be a good fit for you:

- You need to batch process large numbers of location records (geocode, reverse geocode, places & details).
- The license must support commercial use without restrictions.
- It needs to be cheap (or even for free if you don't need more than 6k addresses per day).

Sign up at [geoapify.com](https://geoapify.com/) and start with their free plan of 3k credits per day which translates
to up to 6k address geocodings.

## Install our package with `pip`

This package is available on the public PyPI:

```shell
pip install geobatchpy
```

## Examples

See our documentation at [geobatchpy.readthedocs.io](https://geobatchpy.readthedocs.io/en/latest/) for a growing number of
comprehensive example use cases. Below we illustrate both, the Python API and the CLI, for a tiny batch geocoding
example.

### A simple batch geocoding example using the Python API

Below we geocode multiple addresses in a single batch. There are two ways how we can provide the location data as input.
Either we use a list of strings, one string per address. These are then taken as free text searches. Or we provide
structured input as a list of dictionaries, again one per address. See the
[Geoapify API documentation](https://apidocs.geoapify.com/) for a complete list of address attributes accepted by the
geocoding services. Use the optional `parameters` dictionary if all your addresses have an attribute in common. E.g.,
below we request results in French.

```python
from geobatchpy import Client

client = Client(api_key='<your-api-key>')

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

# see the geoapify.com API docs for more optional parameters
res = client.batch.geocode(locations=addresses, parameters={'lang': 'fr'}, simplify_output=True)
```

Alternatively you can provide a list of dictionaries, with every address in a structured form. And if you still need
the free text search for some, you can do this with the `'text'` attribute. Here is the same example, with the first
two address translated to structured form:

```python
addresses = [{'city': 'Krefeld', 'street': 'Hülser Markt', 'housenumber': 1, 'postcode': '47839'},
             {'name': 'DB Schenker', 'city': 'Essen', 'country': 'Germany'},
             {'text': 'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen'}]
```

```python
# Showing the first of three result sets: res[0]
{
    "query": {
        "text": "Hülser Markt 1, 47839 Krefeld",
        "parsed": {
            "housenumber": "1",
            "street": "hülser markt",
            "postcode": "47839",
            "city": "krefeld",
            "expected_type": "building",
        },
    },
    "datasource": {
        "sourcename": "openstreetmap",
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License",
        "url": "https://www.openstreetmap.org/copyright",
    },
    "name": "Metzgerei Etteldorf",
    "housenumber": "1",
    "street": "Hülser Markt",
    "suburb": "Hüls",
    "city": "Krefeld",
    "state": "Rhénanie-du-Nord-Westphalie",
    "postcode": "47839",
    "country": "Allemagne",
    "country_code": "de",
    "lon": 6.510696417033254,
    "lat": 51.373026800000005,
    "formatted": "Metzgerei Etteldorf, Hülser Markt 1, 47839 Krefeld, Allemagne",
    "address_line1": "Metzgerei Etteldorf",
    "address_line2": "Hülser Markt 1, 47839 Krefeld, Allemagne",
    "category": "commercial.food_and_drink.butcher",
    "result_type": "amenity",
    "rank": {
        "importance": 0.31100000000000005,
        "popularity": 5.585340759145855,
        "confidence": 1,
        "confidence_city_level": 1,
        "confidence_street_level": 1,
        "match_type": "inner_part",
    },
    "place_id": "516b5e6500f40a1a40590a449957bfaf4940f00102f9010ecff70d00000000c002019203134d65747a676572656920457474656c646f7266",
}
```

### The same batch geocoding example using the CLI

We built the `geoapify` command line interface to make batch processing large numbers of records more comfortable.

Steps:
1. Prepare a JSON file as input.
2. Use `geoapify post-batch-jobs` to submit one or more jobs to the Geoapify servers.
3. Use `geoapify monitor-batch-jobs` for monitoring progress and data retrieval.

```python
# Step 1 - written in Python:
from geobatchpy.batch import parse_geocoding_inputs
from geobatchpy.utils import write_data_to_json_file

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

data = {
    'api': '/v1/geocode/search',  # see the Geoapify API docs for other APIs that work with batch processing
    'inputs': parse_geocoding_inputs(locations=addresses),
    'batch_len': 2,  # optional - will put first two addresses in batch 1, last address in batch 2
    'id': 'my-batch-geocoding-job'  # optional - a reference which will be reused in the output file
}

write_data_to_json_file(data=data, file_path='<path-data-in>')
```

The following command submits one or more jobs and stores job URLs to disk. Those URLs are required to monitor
and retrieve results.

```shell
geobatch submit <path-data-in> <path-post-data-out> --api-key <your-key>
```

You can omit the `--api-key` option if you set the `GEOAPIFY_KEY` environment variable. Next we start monitoring
progress:

```shell
geobatch receive <path-post-data-out> <path-results-data-out> --api-key <your-key>
```

We can abort the monitoring at any time and restart later - provided the jobs still are in the cache of
Geoapify servers (24 hours).

## References and further reading

- [geoapify.com API documentation](https://apidocs.geoapify.com/)
- [Towards Data Science - Deduplicate and clean-up millions of location records](https://towardsdatascience.com/deduplicate-and-clean-up-millions-of-location-records-abcffb308ebf)
