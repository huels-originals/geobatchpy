# Python client for the geoapify.com API

This client is in an early stage. We just started and we will contribute several new features, many more geoapify
endpoints, and else in the near future.

## How to install

Install the latest release from public pypi:

```shell
pip install geoapify
```

How to install the current development state from the master branch:

```shell
pip install git+https://github.com/kinsvater/geoapify.git
```

## Batch geocoding example

```python
from geoapify import Client

client = Client(api_key='<your-api-key>', parameters={'lang': 'fr'})  # see the geoapify.com API docs for more options

addresses = ['Hülser Markt 1, 47839 Krefeld',
             'DB Schenker, Essen, Germany',
             'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

res = client.batch_geocode(addresses=addresses)

# Showcase the first of three result sets:
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

## Place Details example

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
                    [7.0093761, 51.450428999],
                    [7.0095574, 51.450353899],
                    [7.0095676, 51.450343499],
                    [7.0095713, 51.450329499],
                    [7.0095657, 51.450316699],
                    [7.0094784, 51.450233899],
                    [7.009469, 51.450223599],
                    [7.0094693, 51.450208399],
                    [7.0094934, 51.450152899],
                    [7.0095066, 51.450144399],
                    [7.0095188, 51.450140599],
                    [7.009538, 51.450139899],
                    [7.0096207, 51.450152399],
                    [7.0096342, 51.450155499],
                    [7.0096446, 51.450160499],
                    [7.0097354, 51.450252499],
                    [7.0097538, 51.450258699],
                    [7.0097791, 51.450262199],
                    [7.0097974, 51.450260099],
                    [7.009934, 51.450205199],
                    [7.0099476, 51.450199899],
                    [7.0099658, 51.450199599],
                    [7.0102431, 51.450236799],
                    [7.0102591, 51.450242899],
                    [7.0102675, 51.450250599],
                    [7.0103502, 51.450335299],
                    [7.0103674, 51.450342999],
                    [7.010387, 51.450345099],
                    [7.0104061, 51.450342399],
                    [7.0105427, 51.450285099],
                    [7.0105585, 51.450282099],
                    [7.0105745, 51.450280899],
                    [7.0106665, 51.450297199],
                    [7.0106825, 51.450307299],
                    [7.0106896, 51.450320699],
                    [7.0106672, 51.450379899],
                    [7.0106593, 51.450388399],
                    [7.0106433, 51.450396199],
                    [7.0105056, 51.450454799],
                    [7.0104961, 51.450466299],
                    [7.0104974, 51.450477999],
                    [7.0105786, 51.450558999],
                    [7.01058, 51.450567899],
                    [7.0105547, 51.450632199],
                    [7.0105382, 51.450638799],
                    [7.0105184, 51.450642299],
                    [7.0104835, 51.450638599],
                    [7.0104218, 51.450629599],
                    [7.0104059, 51.450623199],
                    [7.01035, 51.450572399],
                    [7.0103366, 51.450565699],
                    [7.0102999, 51.450561999],
                    [7.0102799, 51.450563599],
                    [7.0101656, 51.450609599],
                    [7.0101464, 51.450611899],
                    [7.0098273, 51.450568299],
                    [7.0098169, 51.450564099],
                    [7.0097179, 51.450468499],
                    [7.0096988, 51.450461899],
                    [7.0096821, 51.450460399],
                    [7.0096676, 51.450460999],
                    [7.0094924, 51.450531399],
                    [7.0094836, 51.450533799],
                    [7.0094722, 51.450535899],
                    [7.0094542, 51.450535099],
                    [7.0093683, 51.450522199],
                    [7.0093569, 51.450517799],
                    [7.0093494, 51.450508999],
                    [7.0093446, 51.450494299],
                ],
                [
                    [7.0098872, 51.450365899],
                    [7.0098989, 51.450384999],
                    [7.0099838, 51.450464199],
                    [7.0100102, 51.450469499],
                    [7.0100366, 51.450469499],
                    [7.0101765, 51.450410899],
                    [7.0101851, 51.450394999],
                    [7.0101807, 51.450379299],
                    [7.0100945, 51.450291999],
                    [7.0100665, 51.450285699],
                    [7.0100355, 51.450287599],
                    [7.0098966, 51.450346399],
                    [7.0098872, 51.450365899],
                ],
            ],
        },
    },
]
```

## References and further reading

- [geoapify.com API documentation](https://apidocs.geoapify.com/)
- [medium.com - deduplicate and clean-up millions of location records](https://medium.com/@paul.kinsvater/deduplicate-and-clean-up-millions-of-location-records-abcffb308ebf)
