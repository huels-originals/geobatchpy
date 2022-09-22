# Usage examples

## Batch geocoding example

Below we geocode multiple addresses in a single batch. There are two ways how we can provide the location data as input.
Either we use a list of strings, one string per address. These are then taken as free text searches. Or we provide a
structured input by specifying attributes of every address in a dictionary. See the
[Geoapify API documentation](https://apidocs.geoapify.com/) for a complete list of address attributes accepted by the
geocoding services. In both ways, we can also provide structured attributes as optional `parameters`. E.g., below we
asked for results in French.

```python
from geoapify import Client

client = Client(api_key='<your-api-key>', parameters={'lang': 'fr'})  # see the geoapify.com API docs for more options

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

res = client.batch.geocode(locations=addresses, simplify_output=True)
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

## Use the `geoapify` CLI for large jobs

This packages comes with the `geoapify` command line interface. It is useful for executing batch jobs as a daemon or
with little overhead in a terminal.

Before we start, we need to first create a JSON file to store all the inputs. See the
`geoapify.batch.parse_*` functions to bring your inputs into the right format and check the docstrings of
the CLI:

```shell
geoapify post-batch-jobs --help
```

See the following example how to generate a JSON input file for the batch geocoding service using Python:

```python
from geoapify.batch import parse_geocoding_inputs, write_data_to_json_file

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

data = {
    'api': '/v1/geocode/search',  # see the Geoapify API docs for other APIs that work with batch processing
    'inputs': parse_geocoding_inputs(locations=addresses),
    'batch_len': 2,  # optional - will put first two addresses in batch 1, last address in batch 2
    'id': 'my-batch-geocoding-job'  # optional - a reference which will be reused in the output file
}

write_data_to_json_file(data=data, file_path='<path-data-in>')  # use as input for post-batch-jobs
```

Assuming, we have created such data for input, we can post batch processing jobs by

```shell
geoapify post-batch-jobs <path-data-in> <path-post-data-out> --api-key <your-key>
```

You can omit the `--api-key` option if you set your `GEOAPIFY_KEY` environment variable. 

The `post-batch-jobs` should finish rather quickly. Next we can start monitoring progress now or anytime later:

```shell
geoapify monitor-batch-jobs <path-post-data-out> <path-results-data-out> --api-key <your-key>
```

This will monitor the progress of all batch jobs and store results to disk when they all finish. You can abort
this step any time and restart later - provided the jobs still are in cache of the Geoapify servers.

## Place Details example

There is also a batch version of the Place Details API. Below we use the single location version and choose
two different kinds of features in our request. There are many more kinds of features - see the Geoapify docs. But
note that not every location is covered by every kind of feature.

```python
from geoapify import Client

client = Client(api_key='<your-api-key>')

res = client.place_details(latitude=50.8512746, longitude=4.3649087,  # or use place_id (also in geocoding results)
                           features=['details', 'building'])  # defaults to just the 'details' if not specified
res['features']
```

```python
[
    {
        "type": "Feature",
        "properties": {
            "feature_type": "details",
            "name": "Kruppstraße",
            "restrictions": {"max_speed": 30},
            "categories": ["highway", "highway.residential"],
            "datasource": {
                "sourcename": "openstreetmap",
                "attribution": "© OpenStreetMap contributors",
                "license": "Open Database Licence",
                "url": "https://www.openstreetmap.org/copyright",
                "raw": {
                    "lit": "yes",
                    "name": "Kruppstraße",
                    "oneway": "yes",
                    "osm_id": 256731283,
                    "highway": "residential",
                    "surface": "asphalt",
                    "z_order": 330,
                    "maxspeed": 30,
                    "osm_type": "w",
                    "sidewalk": "right",
                    "postal_code": 45128,
                    "lane_markings": "no",
                    "sidewalk:right:surface": "paving_stones",
                },
            },
            "street": "Kruppstraße",
            "city": "Essen",
            "state": "North Rhine-Westphalia",
            "postcode": "45128",
            "country": "Germany",
            "country_code": "de",
            "formatted": "Kruppstraße, 45128 Essen, Germany",
            "address_line1": "Kruppstraße",
            "address_line2": "45128 Essen, Germany",
            "lat": 51.4500523,
            "lon": 7.0093601,
            "place_id": "515b17c8fd580a1c40594bde458c9eb94940f00102f90193684d0f0000000092030c4b7275707073747261c39f65",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [[7.0108501, 51.450249699], [7.0093601, 51.450052299]],
        },
    },
    {
        "type": "Feature",
        "properties": {
            "feature_type": "building",
            "categories": ["building", "building.office", "office", "office.company"],
            "datasource": {
                "sourcename": "openstreetmap",
                "attribution": "© OpenStreetMap contributors",
                "license": "Open Database Licence",
                "url": "https://www.openstreetmap.org/copyright",
                "raw": {
                    "name": "DB Schenker",
                    "office": "company",
                    "osm_id": -7407547,
                    "building": "office",
                    "osm_type": "r",
                    "wikidata": "Q474287",
                    "addr:city": "Essen",
                    "wikipedia": "de:Schenker AG",
                    "roof:shape": "flat",
                    "addr:street": "Kruppstraße",
                    "roof:colour": "black",
                    "addr:country": "DE",
                    "addr:postcode": 45128,
                    "roof:material": "tar_paper",
                    "building:colour": "black",
                    "building:levels": 6,
                    "addr:housenumber": 4,
                    "building:material": "metal",
                },
            },
            "housenumber": "4",
            "street": "Kruppstraße",
            "city": "Essen",
            "state": "North Rhine-Westphalia",
            "postcode": "45128",
            "country": "Germany",
            "country_code": "de",
            "formatted": "DB Schenker, Kruppstraße 4, 45128 Essen, Germany",
            "address_line1": "DB Schenker",
            "address_line2": "Kruppstraße 4, 45128 Essen, Germany",
            "lat": 51.4503917,
            "lon": 7.010418352964237,
            "name": "DB Schenker",
            "wiki_and_media": {"wikidata": "Q474287", "wikipedia": "de:Schenker AG"},
            "building": {
                "levels": 6,
                "type": "office",
                "material": "metal",
                "color": "black",
                "roof": {"shape": "flat", "color": "black"},
            },
            "area": 2622,
            "place_id": "51b6ee06a1420a1c40591c45b8dea6b94940f00101f901bb0771000000000092030b444220536368656e6b6572",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [7.0093446, 51.450494299],
                    [7.0093605, 51.450446299],
                    [7.0093658, 51.450437399],
                    # many more coordinates
                    [7.0093446, 51.450494299],
                ],
                [
                    [7.0098872, 51.450365899],
                    [7.0098989, 51.450384999],
                    [7.0099838, 51.450464199],
                    # many more coordinates
                    [7.0098872, 51.450365899],
                ],
            ],
        },
    },
]
```
