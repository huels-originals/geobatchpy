# Python client for the geoapify.com API

This client is in an early stage. We just started and we will contribute several new features, many more geoapify
endpoints, and else in the near future.

How to install the current development state from the master branch:

## How to install

```shell
pip install git+https://github.com/kinsvater/geoapify.git
```

Install the latest release from public pypi:

```shell
pip install geoapify
```

## Batch geocoding example

```python
from geoapify import Client

client = Client(api_key='<your-api-key>')

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

res = client.batch_geocode(addresses=addresses)
```

## References

- [geoapify.com](https://geoapify.com)
- [medium.com - deduplicate and clean-up millions of location records](https://medium.com/@paul.kinsvater/deduplicate-and-clean-up-millions-of-location-records-abcffb308ebf)
