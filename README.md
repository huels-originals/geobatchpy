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

res[0]
```

```python
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

## References

- [geoapify.com](https://geoapify.com)
- [medium.com - deduplicate and clean-up millions of location records](https://medium.com/@paul.kinsvater/deduplicate-and-clean-up-millions-of-location-records-abcffb308ebf)
