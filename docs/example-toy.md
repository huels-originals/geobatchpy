# Toy examples

## A simple batch geocoding example using the Python API

Below we geocode multiple addresses in a single batch. There are two ways how we can provide the location data as input.
Either we use a list of strings, one string per address. These are then taken as free text searches. Or we provide
structured input as a list of dictionaries, again one per address. See the
[Geoapify API documentation](https://apidocs.geoapify.com/) for a complete list of address attributes accepted by the
geocoding services. Use the optional `parameters` dictionary if all your addresses have an attribute in common. E.g.,
below we request results in French.

```python
from geoapify import Client

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

## The same batch geocoding example using the CLI

Steps:

1. Prepare a JSON file as input.
2. Use `geoapify post-batch-jobs` to submit one or more jobs to the Geoapify servers.
3. Use `geoapify monitor-batch-jobs` for monitoring progress and data retrieval.

```python
# Step 1 - written in Python:
from geoapify.batch import parse_geocoding_inputs
from geoapify.utils import write_data_to_json_file

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

data = {
    'api': '/v1/geocode/search',  # see the Geoapify API docs for other APIs that work with batch processing
    'inputs': parse_geocoding_inputs(locations=addresses),
    'params': {'lang': 'fr'},
    'batch_len': 2,  # optional - will put first two addresses in batch 1, last address in batch 2
    'id': 'my-batch-geocoding-job'  # optional - a reference which will be reused in the output file
}

write_data_to_json_file(data=data, file_path='data-input.json')
```

This short script will create a file with the following content:

```json
{
    "api": "/v1/geocode/search",
    "inputs": [
        {
            "params": {
                "text": "H\u00fclser Markt 1, 47839 Krefeld"
            }
        },
        {
            "params": {
                "text": "DB Schenker, Essen, Germany"
            }
        },
        {
            "params": {
                "text": "JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen"
            }
        }
    ],
    "params": {
        "lang": "fr"
    },
    "batch_len": 2,
    "id": "my-batch-geocoding-job"
}
```

The following command submits one or more jobs. You can omit the `--api-key` option if you set your `GEOAPIFY_KEY`
environment variable.

```shell
geoapify post-batch-jobs data-input.json job-urls.json --api-key <your-key>
```

The last command will create file `job-urls.json` with the following content:

```json
{
    "id": "<some-machine-generated-uuid>",
    "api": "/v1/geocode/search",
    "result_urls": [
        "https://api.geoapify.com/v1/batch?id=<id-of-1st-job>",
        "https://api.geoapify.com/v1/batch?id=<id-of-2nd-job>"
    ],
    "sleep_time": 3,
    "data_input_id": "my-batch-geocoding-job",
    "dt_created": "<date-time-of-creation>"
}
```

Those URLs are required to monitor and retrieve results. Next we start monitoring the progress:

```shell
geoapify monitor-batch-jobs job-urls.json data-output.json --api-key <your-key>
```

We can abort the monitoring at any time and restart later since some jobs take hours to complete. But don't wait for too
long since results are stored not indefinitely long. Assuming, both jobs succeeded, that last command will create file
`data-output.json` with the following content:

```json
{
    "id": "409841fe-703e-4ab6-a513-2e9beaae0797",
    "results": [
        {
            "params": {
                "text": "H\u00fclser Markt 1, 47839 Krefeld"
            },
            "result": {
                "results": [
                    {
                        "datasource": {
                            "sourcename": "openstreetmap",
                            "attribution": "\u00a9 OpenStreetMap contributors",
                            "license": "Open Database License",
                            "url": "https://www.openstreetmap.org/copyright"
                        },
                        "name": "Metzgerei Etteldorf",
                        "housenumber": "1",
                        "street": "H\u00fclser Markt",
                        "suburb": "H\u00fcls",
                        "city": "Krefeld",
                        "state": "Rh\u00e9nanie-du-Nord-Westphalie",
                        "postcode": "47839",
                        "country": "Allemagne",
                        "country_code": "de",
                        "lon": 6.510696417033254,
                        "lat": 51.373026800000005,
                        "formatted": "Metzgerei Etteldorf, H\u00fclser Markt 1, 47839 Krefeld, Allemagne",
                        "address_line1": "Metzgerei Etteldorf",
                        "address_line2": "H\u00fclser Markt 1, 47839 Krefeld, Allemagne",
                        "category": "commercial.food_and_drink.butcher",
                        "timezone": {
                            "name": "Europe/Berlin",
                            "offset_STD": "+01:00",
                            "offset_STD_seconds": 3600,
                            "offset_DST": "+02:00",
                            "offset_DST_seconds": 7200,
                            "abbreviation_STD": "CET",
                            "abbreviation_DST": "CEST"
                        },
                        "result_type": "amenity",
                        "rank": {
                            "importance": 0.31100000000000005,
                            "popularity": 5.585340759145855,
                            "confidence": 1,
                            "confidence_city_level": 1,
                            "confidence_street_level": 1,
                            "match_type": "inner_part"
                        },
                        "place_id": "516b5e6500f40a1a40590a449957bfaf4940f00102f9010ecff70d00000000c002019203134d65747a676572656920457474656c646f7266",
                        "bbox": {
                            "lon1": 6.510585,
                            "lat1": 51.3729539,
                            "lon2": 6.510809,
                            "lat2": 51.3730939
                        }
                    }
                ],
                "query": {
                    "text": "H\u00fclser Markt 1, 47839 Krefeld",
                    "parsed": {
                        "housenumber": "1",
                        "street": "h\u00fclser markt",
                        "postcode": "47839",
                        "city": "krefeld",
                        "expected_type": "building"
                    }
                }
            }
        },
        {
            "params": {
                "text": "DB Schenker, Essen, Germany"
            },
            "result": {
                "results": [
                    {
                        "datasource": {
                            "sourcename": "openstreetmap",
                            "attribution": "\u00a9 OpenStreetMap contributors",
                            "license": "Open Database License",
                            "url": "https://www.openstreetmap.org/copyright"
                        },
                        "name": "DB Schenker",
                        "housenumber": "4",
                        "street": "Kruppstra\u00dfe",
                        "suburb": "Sternviertel",
                        "district": "Stadtbezirk I",
                        "city": "Essen",
                        "state": "Rh\u00e9nanie-du-Nord-Westphalie",
                        "postcode": "45128",
                        "country": "Allemagne",
                        "country_code": "de",
                        "lon": 7.010418352964237,
                        "lat": 51.4503917,
                        "formatted": "DB Schenker, Kruppstra\u00dfe 4, 45128 Essen, Allemagne",
                        "address_line1": "DB Schenker",
                        "address_line2": "Kruppstra\u00dfe 4, 45128 Essen, Allemagne",
                        "timezone": {
                            "name": "Europe/Berlin",
                            "offset_STD": "+01:00",
                            "offset_STD_seconds": 3600,
                            "offset_DST": "+02:00",
                            "offset_DST_seconds": 7200,
                            "abbreviation_STD": "CET",
                            "abbreviation_DST": "CEST"
                        },
                        "result_type": "amenity",
                        "rank": {
                            "importance": 0.5995218989809716,
                            "popularity": 8.464778201466588,
                            "confidence": 1,
                            "confidence_city_level": 1,
                            "match_type": "full_match"
                        },
                        "place_id": "51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb07710000000000c0020192030b444220536368656e6b6572",
                        "bbox": {
                            "lon1": 7.0093446,
                            "lat1": 51.4501399,
                            "lon2": 7.0106896,
                            "lat2": 51.4506423
                        }
                    },
                    {
                        "datasource": {
                            "sourcename": "openstreetmap",
                            "attribution": "\u00a9 OpenStreetMap contributors",
                            "license": "Open Database License",
                            "url": "https://www.openstreetmap.org/copyright"
                        },
                        "name": "DB Schenker",
                        "housenumber": "81",
                        "street": "Alfredstra\u00dfe",
                        "suburb": "R\u00fcttenscheid",
                        "district": "Stadtbezirk II",
                        "city": "Essen",
                        "state": "Rh\u00e9nanie-du-Nord-Westphalie",
                        "postcode": "45130",
                        "country": "Allemagne",
                        "country_code": "de",
                        "lon": 7.002773,
                        "lat": 51.4346836,
                        "formatted": "DB Schenker, Alfredstra\u00dfe 81, 45130 Essen, Allemagne",
                        "address_line1": "DB Schenker",
                        "address_line2": "Alfredstra\u00dfe 81, 45130 Essen, Allemagne",
                        "timezone": {
                            "name": "Europe/Berlin",
                            "offset_STD": "+01:00",
                            "offset_STD_seconds": 3600,
                            "offset_DST": "+02:00",
                            "offset_DST_seconds": 7200,
                            "abbreviation_STD": "CET",
                            "abbreviation_DST": "CEST"
                        },
                        "result_type": "amenity",
                        "rank": {
                            "importance": 0.30100000000000005,
                            "popularity": 7.729958748897548,
                            "confidence": 1,
                            "confidence_city_level": 1,
                            "match_type": "full_match"
                        },
                        "place_id": "514b3fe1ecd6021c4059c40d53b6a3b74940f00103f901ba6be90501000000c0020192030b444220536368656e6b6572",
                        "bbox": {
                            "lon1": 7.002723,
                            "lat1": 51.4346336,
                            "lon2": 7.002823,
                            "lat2": 51.4347336
                        }
                    }
                ],
                "query": {
                    "text": "DB Schenker, Essen, Germany",
                    "parsed": {
                        "house": "db schenker",
                        "city": "essen",
                        "country": "germany",
                        "expected_type": "amenity"
                    }
                }
            }
        },
        {
            "params": {
                "text": "JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen"
            },
            "result": {
                "results": [
                    {
                        "datasource": {
                            "sourcename": "openstreetmap",
                            "attribution": "\u00a9 OpenStreetMap contributors",
                            "license": "Open Database License",
                            "url": "https://www.openstreetmap.org/copyright"
                        },
                        "housenumber": "5",
                        "street": "Am Schimmersfeld",
                        "suburb": "Tiefenbroich",
                        "city": "Ratingen",
                        "county": "Kreis Mettmann",
                        "state": "Rh\u00e9nanie-du-Nord-Westphalie",
                        "postcode": "40880",
                        "country": "Allemagne",
                        "country_code": "de",
                        "lon": 6.8305828,
                        "lat": 51.3015775,
                        "formatted": "Am Schimmersfeld 5, 40880 Ratingen, Allemagne",
                        "address_line1": "Am Schimmersfeld 5",
                        "address_line2": "40880 Ratingen, Allemagne",
                        "timezone": {
                            "name": "Europe/Berlin",
                            "offset_STD": "+01:00",
                            "offset_STD_seconds": 3600,
                            "offset_DST": "+02:00",
                            "offset_DST_seconds": 7200,
                            "abbreviation_STD": "CET",
                            "abbreviation_DST": "CEST"
                        },
                        "result_type": "building",
                        "rank": {
                            "importance": 0.31100000000000005,
                            "popularity": 6.432032060963271,
                            "confidence": 0.9,
                            "confidence_city_level": 1,
                            "confidence_street_level": 1,
                            "match_type": "match_by_building"
                        },
                        "place_id": "51fe7a2a4c84521b4059cfda6d179aa64940f00103f9015f2517b900000000c00203",
                        "bbox": {
                            "lon1": 6.8305328,
                            "lat1": 51.3015275,
                            "lon2": 6.8306328,
                            "lat2": 51.3016275
                        }
                    }
                ],
                "query": {
                    "text": "JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen",
                    "parsed": {
                        "house": "jci beteiligungs gmbh",
                        "housenumber": "5",
                        "street": "am schimmersfeld",
                        "city": "ratingen",
                        "expected_type": "amenity"
                    }
                }
            }
        }
    ],
    "data_input_id": "5ce4e761-4c77-4b4b-b196-690d852ccd33",
    "dt_created": "2022-10-11 14:36:15.260914"
}
```

This is where the responsibility of our package ends. Are you curious about how to parse the data for analytics in
Python? Check out our [comprehensive batch processing tutorial](tutorial-enrich-locations.ipynb).

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
