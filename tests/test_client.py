import logging

import requests

from geoapify.client import Client

logging.basicConfig(level=logging.DEBUG)

content_ind = 0


class TestClient:
    API_KEY = 'not-required-since-we-mock'

    def test_places(self, monkeypatch):
        class MockRequestsGet:
            def __init__(self, url, params, headers):
                pass

            @staticmethod
            def json():
                return RES_TEST_PLACES

        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        res = client.places(
            categories=['accommodation.hotel', 'accommodation.hostel', 'accommodation.motel'],
            filter_by_region='rect:11.563106549898483,48.12898913611139,11.57704581350751,48.13666585409989', limit=3
        )

        assert len(res['features']) == 3
        assert res['features'][0]['properties']['city'] == 'Munich'

    def test_place_details(self, monkeypatch):
        class MockRequestsGet:
            def __init__(self, url, params, headers):
                pass

            @staticmethod
            def json():
                return RES_TEST_PLACE_DETAILS

        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        place_id = '517f1a52a0aa751140592f75eb90f66c4940f00103f901727' \
                   'c302101000000c0020192030d486f74656c204173746f726961'
        res = client.place_details(place_id=place_id)

        monkeypatch.setattr(MockRequestsGet, 'json', lambda _: RES_TEST_PLACE_DETAILS_2)

        lat, lon = 50.8512746, 4.3649087
        res2 = client.place_details(latitude=lat, longitude=lon)

        assert res['features'][0]['properties']['street'] == res2['features'][0]['properties']['street']

    def test_geocode(self, monkeypatch):
        # monkey patching class
        class MockRequestsGet:
            def __init__(self, url, params, headers):
                pass

            @staticmethod
            def json():
                return RES_TEST_GEOCODE

        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        res = client.geocode(text='Hülser Markt 1, 47839 Krefeld')

        # update monkey patch for second call
        monkeypatch.setattr(MockRequestsGet, 'json', lambda _: RES_TEST_GEOCODE_2)

        res2 = client.geocode(parameters={'name': 'DB Schenker', 'city': 'Essen', 'country': 'Germany'})

        assert res['features'][0]['properties']['suburb'] == 'Hüls'
        assert res2['features'][0]['properties']['street'] == 'Kruppstraße'

    def test_reverse_geocode(self, monkeypatch):
        class MockRequestsGet:
            def __init__(self, url, params, headers):
                pass

            @staticmethod
            def json():
                return RES_TEST_REVERSE_GEOCODE

        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        res = client.reverse_geocode(latitude=51.450216, longitude=7.010232)

        assert res['features'][0]['properties']['name'] == 'DB Schenker'

    def test_batch_geocode(self, monkeypatch):
        class MockRequestsPost:
            def __init__(self, request_url, json, headers):
                self.status_code = 200

            @staticmethod
            def json():
                return {'url': ''}

        global content_ind
        content_ind = -1

        class MockRequestsGet:
            def __init__(self, url, headers):
                pass

            def json(self):
                global content_ind
                content_ind += 1
                return RES_TEST_BATCH_GEOCODE[content_ind]

        monkeypatch.setattr(requests, 'post', MockRequestsPost)
        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        addresses = ['Hülser Markt 1, 47839 Krefeld', 'DB Schenker, Essen, Germany',
                     'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

        res = client.batch.geocode(locations=addresses, batch_len=2, parameters={'lang': 'fr'}, simplify_output=True)

        assert len(res) == len(addresses)
        assert res[0]['housenumber'] == '1'
        assert res[1]['city'] == 'Essen'
        assert res[2]['country'] == 'Allemagne'

    def test_batch_reverse_geocode(self, monkeypatch):
        class MockRequestsPost:
            def __init__(self, request_url, json, headers):
                self.status_code = 200

            @staticmethod
            def json():
                return {'url': ''}

        global content_ind
        content_ind = -1

        class MockRequestsGet:

            def __init__(self, url, headers):
                pass

            @staticmethod
            def json():
                global content_ind
                content_ind += 1
                return RES_TEST_BATCH_REVERSE_GEOCODE[content_ind]

        monkeypatch.setattr(requests, 'post', MockRequestsPost)
        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        geocodes = [(7.010232, 51.450216), (4.3649087, 50.8512746), (30.215443, 50.554534)]

        res = client.batch.reverse_geocode(geocodes=geocodes, batch_len=2, simplify_output=True)

        assert len(res) == len(geocodes)
        assert res[0]['name'] == 'DB Schenker'
        assert res[1]['country'] == 'Belgium'
        assert res[2]['city'] == 'Bucha'

    def test_batch_places(self, monkeypatch):
        class MockRequestsPost:
            def __init__(self, request_url, json, headers):
                self.status_code = 200

            @staticmethod
            def json():
                return {'url': ''}

        global content_ind
        content_ind = -1

        class MockRequestsGet:

            def __init__(self, url, headers):
                pass

            @staticmethod
            def json():
                return RES_TEST_BATCH_PLACES[0]

        monkeypatch.setattr(requests, 'post', MockRequestsPost)
        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        ind_params = [
            {'filter': 'rect:11.563106549898483,48.12898913611139,11.57704581350751,48.13666585409989',
             'conditions': 'named'},
            {'filter': 'circle:7.010232,51.450216,3000'}
        ]

        params = {'categories': ['accommodation.hotel', 'accommodation.hostel', 'accommodation.motel'],
                  'limit': 3}

        res = client.batch.places(individual_parameters=ind_params, parameters=params)

        assert len(res) == 2
        assert len(res[0]['result']['features']) == 3
        assert res[0]['result']['features'][2]['properties']['city'] == 'Munich'

    def test_batch_place_details(self, monkeypatch):
        class MockRequestsPost:
            def __init__(self, request_url, json, headers):
                self.status_code = 200

            @staticmethod
            def json():
                return {'url': ''}

        global content_ind
        content_ind = -1

        class MockRequestsGet:

            def __init__(self, url, headers):
                pass

            @staticmethod
            def json():
                global content_ind
                content_ind += 1
                return RES_TEST_BATCH_PLACE_DETAILS[content_ind]

        monkeypatch.setattr(requests, 'post', MockRequestsPost)
        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        geocodes = [(7.010232, 51.450216), (4.3649087, 50.8512746), (30.215443, 50.554534)]

        res = client.batch.place_details(geocodes=geocodes, batch_len=2)

        assert len(res[0]['result']['features']) == 2
        building_properties_1 = res[1]['result']['features'][1]['properties']
        assert building_properties_1['feature_type'] == 'building'
        assert building_properties_1['country'] == 'Belgium'
        details_properties_2 = res[2]['result']['features'][0]['properties']
        assert details_properties_2['feature_type'] == 'details'
        assert details_properties_2['city'] == 'Bucha'


# API responses of the tests:
RES_TEST_PLACES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Deutsche Eiche",
                "housenumber": "13",
                "street": "Reichenbachstraße",
                "neighbourhood": "Gärtnerplatz",
                "suburb": "Gärtnerplatz",
                "district": "Ludwigsvorstadt-Isarvorstadt",
                "city": "Munich",
                "state": "Bavaria",
                "postcode": "80469",
                "country": "Germany",
                "country_code": "de",
                "lon": 11.576359869215747,
                "lat": 48.132741550000006,
                "formatted": "Deutsche Eiche, Reichenbachstraße 13, 80469 Munich, Germany",
                "address_line1": "Deutsche Eiche",
                "address_line2": "Reichenbachstraße 13, 80469 Munich, Germany",
                "categories": [
                    "accommodation",
                    "accommodation.hotel",
                    "building",
                    "building.accommodation",
                    "wheelchair",
                    "wheelchair.limited",
                ],
                "details": [
                    "details",
                    "details.accommodation",
                    "details.building",
                    "details.contact",
                    "details.facilities",
                    "details.wiki_and_media",
                ],
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database Licence",
                    "url": "https://www.openstreetmap.org/copyright",
                    "raw": {
                        "name": "Deutsche Eiche",
                        "lgbtq": "primary",
                        "stars": "3S",
                        "osm_id": 99876859,
                        "tourism": "hotel",
                        "website": "https://www.deutsche-eiche.com/",
                        "building": "yes",
                        "operator": "Josef Sattler GmbH",
                        "osm_type": "w",
                        "wikidata": "Q1630878",
                        "addr:city": "München",
                        "wikipedia": "de:Hotel Deutsche Eiche",
                        "start_date": 1864,
                        "wheelchair": "limited",
                        "addr:street": "Reichenbachstraße",
                        "contact:fax": " 49 89 23116698",
                        "addr:country": "DE",
                        "addr:postcode": 80469,
                        "contact:email": "info@deutsche-eiche.com",
                        "contact:phone": " 49 89 2311660",
                        "addr:housenumber": 13,
                    },
                },
                "place_id": "51efd7d3a4182727405994dd03acfd104840f00102f901fbfff3050000000092030e4465757473636865204569636865",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [11.57635989271145, 48.13274145306346],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Hotel Atlanta",
                "housenumber": "58",
                "street": "Sendlinger Straße",
                "quarter": "Hackenviertel",
                "suburb": "Altstadt-Lehel",
                "city": "Munich",
                "state": "Bavaria",
                "postcode": "80331",
                "country": "Germany",
                "country_code": "de",
                "lon": 11.56825361565961,
                "lat": 48.13447675,
                "formatted": "Hotel Atlanta, Sendlinger Straße 58, 80331 Munich, Germany",
                "address_line1": "Hotel Atlanta",
                "address_line2": "Sendlinger Straße 58, 80331 Munich, Germany",
                "categories": [
                    "accommodation",
                    "accommodation.hotel",
                    "building",
                    "building.accommodation",
                    "building.residential",
                    "internet_access",
                    "internet_access.free",
                ],
                "details": [
                    "details",
                    "details.accommodation",
                    "details.contact",
                    "details.facilities",
                ],
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database Licence",
                    "url": "https://www.openstreetmap.org/copyright",
                    "raw": {
                        "fax": " 49 89 2609027",
                        "name": "Hotel Atlanta",
                        "email": "info@hotel-atlanta.de",
                        "phone": " 49 89 263605",
                        "stars": 2,
                        "osm_id": 55800408,
                        "smoking": "no",
                        "tourism": "hotel",
                        "website": "http://www.hotel-atlanta.de/",
                        "building": "apartments",
                        "osm_type": "w",
                        "addr:city": "München",
                        "addr:street": "Sendlinger Straße",
                        "addr:country": "DE",
                        "addr:postcode": 80331,
                        "internet_access": "wlan",
                        "addr:housenumber": 58,
                        "internet_access:fee": "no",
                    },
                },
                "place_id": "516b60c1d2ec22274059cc86883f37114840f00102f901587253030000000092030d486f74656c2041746c616e7461",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [11.56821306810908, 48.134498540557246],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude",
                "housenumber": "18",
                "street": "Kreuzstraße",
                "quarter": "Hackenviertel",
                "suburb": "Altstadt-Lehel",
                "city": "Munich",
                "state": "Bavaria",
                "postcode": "80331",
                "country": "Germany",
                "country_code": "de",
                "lon": 11.5675918,
                "lat": 48.135158,
                "formatted": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude, Kreuzstraße 18, 80331 Munich, Germany",
                "address_line1": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude",
                "address_line2": "Kreuzstraße 18, 80331 Munich, Germany",
                "categories": [
                    "accommodation",
                    "accommodation.hotel",
                    "internet_access",
                ],
                "details": [
                    "details",
                    "details.accommodation",
                    "details.contact",
                    "details.facilities",
                ],
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database Licence",
                    "url": "https://www.openstreetmap.org/copyright",
                    "raw": {
                        "fax": " 49 89 23036701",
                        "name": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude",
                        "email": "info@herzog-wilhelm.de",
                        "phone": " 49 89 230360",
                        "stars": 3,
                        "osm_id": 305433531,
                        "tourism": "hotel",
                        "website": "http://www.herzog-wilhelm.de",
                        "operator": "Herzog-Wilhelm-Restaurant-Tannenbaum GmbH",
                        "osm_type": "n",
                        "addr:city": "München",
                        "addr:street": "Kreuzstraße",
                        "addr:country": "DE",
                        "addr:postcode": 80331,
                        "internet_access": "wlan",
                        "addr:housenumber": 18,
                    },
                },
                "place_id": "51a0f474649b2227405963b17adb4c114840f00103f901bb8b34120000000092032d486f74656c204865727a6f672057696c68656c6d2054616e6e656e6261756d204e6562656e676562c3a4756465",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [11.567591800000002, 48.13515799990525],
            },
        },
    ],
}

RES_TEST_PLACE_DETAILS = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "feature_type": "details",
                "description": "Renovation pending - expected to be opened again by 2019",
                "name": "Hotel Astoria",
                "wiki_and_media": {"wikidata": "Q649690"},
                "categories": [],
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database Licence",
                    "url": "https://www.openstreetmap.org/copyright",
                    "raw": {
                        "name": "Hotel Astoria",
                        "osm_id": 4851793010,
                        "osm_type": "n",
                        "wikidata": "Q649690",
                        "addr:city": "Bruxelles - Brussel",
                        "addr:street": "Rue Royale - Koningsstraat",
                        "description": "Renovation pending - expected to be opened again by 2019",
                        "addr:country": "BE",
                        "addr:postcode": 1000,
                        "disused:tourism": "hotel",
                        "addr:housenumber": 103,
                    },
                },
                "housenumber": "103",
                "street": "Rue Royale - Koningsstraat",
                "city": "City of Brussels",
                "county": "Brussels-Capital",
                "state": "Brussels-Capital",
                "postcode": "1000",
                "country": "Belgium",
                "country_code": "be",
                "formatted": "Hotel Astoria, Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium",
                "address_line1": "Hotel Astoria",
                "address_line2": "Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium",
                "lat": 50.8512746,
                "lon": 4.3649087,
                "place_id": "517f1a52a0aa7511405923e7e990f66c4940f00103f901727c30210100000092030d486f74656c204173746f726961",
            },
            "geometry": {"type": "Point", "coordinates": [4.3649087, 50.851274599]},
        }
    ],
}
RES_TEST_PLACE_DETAILS_2 = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "feature_type": "details",
                "website": "https://www.corinthia.com/brussels/",
                "description": "https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld",
                "name": "Corinthia Grand Hôtel Astoria",
                "wiki_and_media": {
                    "wikidata": "Q649690",
                    "wikipedia": "en:Hotel Astoria, Brussels",
                },
                "building": {"type": "construction"},
                "categories": ["building"],
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database Licence",
                    "url": "https://www.openstreetmap.org/copyright",
                    "raw": {
                        "name": "Corinthia Grand Hôtel Astoria",
                        "osm_id": -2999762,
                        "website": "https://www.corinthia.com/brussels/",
                        "building": "construction",
                        "osm_type": "r",
                        "wikidata": "Q649690",
                        "wikipedia": "en:Hotel Astoria, Brussels",
                        "description": "https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld",
                        "opening_date": "2024-06-01",
                        "proposed:tourism": "hotel",
                    },
                },
                "street": "Rue Royale - Koningsstraat",
                "city": "City of Brussels",
                "county": "Brussels-Capital",
                "state": "Brussels-Capital",
                "postcode": "1000",
                "country": "Belgium",
                "country_code": "be",
                "formatted": "Corinthia Grand Hôtel Astoria, Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium",
                "address_line1": "Corinthia Grand Hôtel Astoria",
                "address_line2": "Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium",
                "lat": 50.851208150000005,
                "lon": 4.3654038908803035,
                "place_id": "5177d3b20af9751140590a9a9800f46c4940f00101f901d2c52d000000000092031e436f72696e74686961204772616e642048c3b474656c204173746f726961",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [4.3647787, 50.851130099],
                        [4.3649217, 50.851094499],
                        [4.3649394, 50.851130799],
                        [4.3649988, 50.851119199],
                        [4.3649796, 50.851079999],
                        [4.3651534, 50.851036699],
                        [4.3651721, 50.851077699],
                        [4.3652199, 50.851065799],
                        [4.3652006, 50.851024899],
                        [4.3652285, 50.851017999],
                        [4.3652901, 50.851003699],
                        [4.3653076, 50.850999299],
                        [4.3653419, 50.850990399],
                        [4.3653824, 50.850980099],
                        [4.3654073, 50.850973899],
                        [4.3654312, 50.850967499],
                        [4.3654639, 50.850960199],
                        [4.3654869, 50.850992299],
                        [4.365563, 50.851098099],
                        [4.3655807, 50.851124499],
                        [4.3655598, 50.851186599],
                        [4.3655858, 50.851190599],
                        [4.3655713, 50.851233599],
                        [4.3655242, 50.851225699],
                        [4.3655116, 50.851226199],
                        [4.365509, 50.851233599],
                        [4.365518, 50.851231799],
                        [4.365551, 50.851295699],
                        [4.3655273, 50.851300599],
                        [4.3655137, 50.851302599],
                        [4.3653644, 50.851339299],
                        [4.3653426, 50.851298399],
                        [4.3652968, 50.851308299],
                        [4.3653189, 50.851350399],
                        [4.3652015, 50.851379499],
                        [4.3651893, 50.851355599],
                        [4.3651634, 50.851361399],
                        [4.3651776, 50.851385899],
                        [4.3651334, 50.851395799],
                        [4.3651193, 50.851369099],
                        [4.3651023, 50.851372899],
                        [4.3650939, 50.851356599],
                        [4.3650595, 50.851363299],
                        [4.365081, 50.851406499],
                        [4.3649381, 50.851436899],
                        [4.3647787, 50.851130099],
                    ],
                    [
                        [4.3650345, 50.851161199],
                        [4.3651073, 50.851299499],
                        [4.3651238, 50.851295999],
                        [4.3651158, 50.851280099],
                        [4.3652348, 50.851255299],
                        [4.3652436, 50.851271899],
                        [4.3652588, 50.851268899],
                        [4.3651882, 50.851130099],
                        [4.3650345, 50.851161199],
                    ],
                ],
            },
        }
    ],
}
RES_TEST_GEOCODE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
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
                "state": "North Rhine-Westphalia",
                "postcode": "47839",
                "country": "Germany",
                "country_code": "de",
                "lon": 6.510696417033254,
                "lat": 51.373026800000005,
                "formatted": "Metzgerei Etteldorf, Hülser Markt 1, 47839 Krefeld, Germany",
                "address_line1": "Metzgerei Etteldorf",
                "address_line2": "Hülser Markt 1, 47839 Krefeld, Germany",
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
            },
            "geometry": {
                "type": "Point",
                "coordinates": [6.510696417033254, 51.373026800000005],
            },
            "bbox": [6.510585, 51.3729539, 6.510809, 51.3730939],
        }
    ],
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
}

RES_TEST_GEOCODE_2 = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database License",
                    "url": "https://www.openstreetmap.org/copyright",
                },
                "name": "DB Schenker",
                "housenumber": "4",
                "street": "Kruppstraße",
                "suburb": "Sternviertel",
                "district": "Stadtbezirk I",
                "city": "Essen",
                "state": "North Rhine-Westphalia",
                "postcode": "45128",
                "country": "Germany",
                "country_code": "de",
                "lon": 7.010418352964237,
                "lat": 51.4503917,
                "formatted": "DB Schenker, Kruppstraße 4, 45128 Essen, Germany",
                "address_line1": "DB Schenker",
                "address_line2": "Kruppstraße 4, 45128 Essen, Germany",
                "result_type": "amenity",
                "rank": {
                    "importance": 0.7195218989809715,
                    "popularity": 8.464778201466588,
                    "confidence": 1,
                    "confidence_city_level": 1,
                    "match_type": "full_match",
                },
                "place_id": "51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb07710000000000c0020192030b444220536368656e6b6572",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [7.010418352964237, 51.4503917],
            },
            "bbox": [7.0093446, 51.4501399, 7.0106896, 51.4506423],
        },
        {
            "type": "Feature",
            "properties": {
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database License",
                    "url": "https://www.openstreetmap.org/copyright",
                },
                "name": "DB Schenker",
                "housenumber": "81",
                "street": "Alfredstraße",
                "suburb": "Rüttenscheid",
                "district": "Stadtbezirk II",
                "city": "Essen",
                "state": "North Rhine-Westphalia",
                "postcode": "45130",
                "country": "Germany",
                "country_code": "de",
                "lon": 7.002773,
                "lat": 51.4346836,
                "formatted": "DB Schenker, Alfredstraße 81, 45130 Essen, Germany",
                "address_line1": "DB Schenker",
                "address_line2": "Alfredstraße 81, 45130 Essen, Germany",
                "result_type": "amenity",
                "rank": {
                    "importance": 0.42099999999999993,
                    "popularity": 7.729958748897548,
                    "confidence": 1,
                    "confidence_city_level": 1,
                    "match_type": "full_match",
                },
                "place_id": "514b3fe1ecd6021c4059c40d53b6a3b74940f00103f901ba6be90501000000c0020192030b444220536368656e6b6572",
            },
            "geometry": {"type": "Point", "coordinates": [7.002773, 51.4346836]},
            "bbox": [7.002723, 51.4346336, 7.002823, 51.4347336],
        },
    ],
    "query": {
        "text": "",
        "parsed": {
            "house": "DB Schenker",
            "city": "Essen",
            "country": "Germany",
            "expected_type": "amenity",
        },
    },
}
RES_TEST_REVERSE_GEOCODE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "datasource": {
                    "sourcename": "openstreetmap",
                    "attribution": "© OpenStreetMap contributors",
                    "license": "Open Database License",
                    "url": "https://www.openstreetmap.org/copyright",
                },
                "name": "DB Schenker",
                "housenumber": "4",
                "street": "Kruppstraße",
                "suburb": "Sternviertel",
                "district": "Stadtbezirk I",
                "city": "Essen",
                "state": "North Rhine-Westphalia",
                "postcode": "45128",
                "country": "Germany",
                "country_code": "de",
                "lon": 7.010418352964237,
                "lat": 51.4503917,
                "distance": 2.09919434696081,
                "result_type": "amenity",
                "county": "Essen",
                "formatted": "DB Schenker, Kruppstraße 4, 45128 Essen, Germany",
                "address_line1": "DB Schenker",
                "address_line2": "Kruppstraße 4, 45128 Essen, Germany",
                "rank": {
                    "importance": 0.29952189898097165,
                    "popularity": 8.464778201466588,
                },
                "place_id": "51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb0771000000000092030b444220536368656e6b6572e203246f70656e7374726565746d61703a76656e75653a72656c6174696f6e2f37343037353437",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [7.010418352964237, 51.4503917],
            },
            "bbox": [7.0093446, 51.4501399, 7.0106896, 51.4506423],
        }
    ],
}
RES_TEST_BATCH_GEOCODE = [
    {
        "api": "/v1/geocode/search",
        "params": {"format": "json", "lang": "fr"},
        "id": "075271f090ad4bd4a578827296fa214b",
        "results": [
            {
                "params": {"text": "Hülser Markt 1, 47839 Krefeld"},
                "result": {
                    "results": [
                        {
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
                            "bbox": {
                                "lon1": 6.510585,
                                "lat1": 51.3729539,
                                "lon2": 6.510809,
                                "lat2": 51.3730939,
                            },
                        }
                    ],
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
                },
            },
            {
                "params": {"text": "DB Schenker, Essen, Germany"},
                "result": {
                    "results": [
                        {
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database License",
                                "url": "https://www.openstreetmap.org/copyright",
                            },
                            "name": "DB Schenker",
                            "housenumber": "4",
                            "street": "Kruppstraße",
                            "suburb": "Sternviertel",
                            "district": "Stadtbezirk I",
                            "city": "Essen",
                            "state": "Rhénanie-du-Nord-Westphalie",
                            "postcode": "45128",
                            "country": "Allemagne",
                            "country_code": "de",
                            "lon": 7.010418352964237,
                            "lat": 51.4503917,
                            "formatted": "DB Schenker, Kruppstraße 4, 45128 Essen, Allemagne",
                            "address_line1": "DB Schenker",
                            "address_line2": "Kruppstraße 4, 45128 Essen, Allemagne",
                            "result_type": "amenity",
                            "rank": {
                                "importance": 0.5995218989809716,
                                "popularity": 8.464778201466588,
                                "confidence": 1,
                                "confidence_city_level": 1,
                                "match_type": "full_match",
                            },
                            "place_id": "51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb07710000000000c0020192030b444220536368656e6b6572",
                            "bbox": {
                                "lon1": 7.0093446,
                                "lat1": 51.4501399,
                                "lon2": 7.0106896,
                                "lat2": 51.4506423,
                            },
                        },
                        {
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database License",
                                "url": "https://www.openstreetmap.org/copyright",
                            },
                            "name": "DB Schenker",
                            "housenumber": "81",
                            "street": "Alfredstraße",
                            "suburb": "Rüttenscheid",
                            "district": "Stadtbezirk II",
                            "city": "Essen",
                            "state": "Rhénanie-du-Nord-Westphalie",
                            "postcode": "45130",
                            "country": "Allemagne",
                            "country_code": "de",
                            "lon": 7.002773,
                            "lat": 51.4346836,
                            "formatted": "DB Schenker, Alfredstraße 81, 45130 Essen, Allemagne",
                            "address_line1": "DB Schenker",
                            "address_line2": "Alfredstraße 81, 45130 Essen, Allemagne",
                            "result_type": "amenity",
                            "rank": {
                                "importance": 0.30100000000000005,
                                "popularity": 7.729958748897548,
                                "confidence": 1,
                                "confidence_city_level": 1,
                                "match_type": "full_match",
                            },
                            "place_id": "514b3fe1ecd6021c4059c40d53b6a3b74940f00103f901ba6be90501000000c0020192030b444220536368656e6b6572",
                            "bbox": {
                                "lon1": 7.002723,
                                "lat1": 51.4346336,
                                "lon2": 7.002823,
                                "lat2": 51.4347336,
                            },
                        },
                    ],
                    "query": {
                        "text": "DB Schenker, Essen, Germany",
                        "parsed": {
                            "house": "db schenker",
                            "city": "essen",
                            "country": "germany",
                            "expected_type": "amenity",
                        },
                    },
                },
            },
        ],
    },
    {
        "api": "/v1/geocode/search",
        "params": {"format": "json", "lang": "fr"},
        "id": "9b885b64ead44ba4b36b1aae222f380a",
        "results": [
            {
                "params": {"text": "JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen"},
                "result": {
                    "results": [
                        {
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database License",
                                "url": "https://www.openstreetmap.org/copyright",
                            },
                            "housenumber": "5",
                            "street": "Am Schimmersfeld",
                            "suburb": "Tiefenbroich",
                            "city": "Ratingen",
                            "county": "Kreis Mettmann",
                            "state": "Rhénanie-du-Nord-Westphalie",
                            "postcode": "40880",
                            "country": "Allemagne",
                            "country_code": "de",
                            "lon": 6.8305828,
                            "lat": 51.3015775,
                            "formatted": "Am Schimmersfeld 5, 40880 Ratingen, Allemagne",
                            "address_line1": "Am Schimmersfeld 5",
                            "address_line2": "40880 Ratingen, Allemagne",
                            "result_type": "building",
                            "rank": {
                                "importance": 0.31100000000000005,
                                "popularity": 6.432032060963271,
                                "confidence": 0.9,
                                "confidence_city_level": 1,
                                "confidence_street_level": 1,
                                "match_type": "match_by_building",
                            },
                            "place_id": "51fe7a2a4c84521b4059cfda6d179aa64940f00103f9015f2517b900000000c00203",
                            "bbox": {
                                "lon1": 6.8305328,
                                "lat1": 51.3015275,
                                "lon2": 6.8306328,
                                "lat2": 51.3016275,
                            },
                        }
                    ],
                    "query": {
                        "text": "JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen",
                        "parsed": {
                            "house": "jci beteiligungs gmbh",
                            "housenumber": "5",
                            "street": "am schimmersfeld",
                            "city": "ratingen",
                            "expected_type": "amenity",
                        }
                    }
                }
            }
        ]
    }]

RES_TEST_BATCH_REVERSE_GEOCODE = [
    {
        "api": "/v1/geocode/reverse",
        "params": {"format": "json"},
        "id": "305eb599399046e2a37a7e21a88850f2",
        "results": [
            {
                "params": {"lat": 51.450216, "lon": 7.010232},
                "result": {
                    "results": [
                        {
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database License",
                                "url": "https://www.openstreetmap.org/copyright",
                            },
                            "name": "DB Schenker",
                            "housenumber": "4",
                            "street": "Kruppstraße",
                            "suburb": "Sternviertel",
                            "district": "Stadtbezirk I",
                            "city": "Essen",
                            "state": "North Rhine-Westphalia",
                            "postcode": "45128",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 7.010418352964237,
                            "lat": 51.4503917,
                            "distance": 2.09919434696081,
                            "result_type": "amenity",
                            "county": "Essen",
                            "formatted": "DB Schenker, Kruppstraße 4, 45128 Essen, Germany",
                            "address_line1": "DB Schenker",
                            "address_line2": "Kruppstraße 4, 45128 Essen, Germany",
                            "rank": {
                                "importance": 0.29952189898097165,
                                "popularity": 8.464778201466588,
                            },
                            "place_id": "51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb0771000000000092030b444220536368656e6b6572e203246f70656e7374726565746d61703a76656e75653a72656c6174696f6e2f37343037353437",
                            "bbox": {
                                "lon1": 7.0093446,
                                "lat1": 51.4501399,
                                "lon2": 7.0106896,
                                "lat2": 51.4506423,
                            },
                        }
                    ]
                },
            },
            {
                "params": {"lat": 50.8512746, "lon": 4.3649087},
                "result": {
                    "results": [
                        {
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database License",
                                "url": "https://www.openstreetmap.org/copyright",
                            },
                            "name": "Corinthia Grand Hôtel Astoria",
                            "street": "Rue Royale - Koningsstraat",
                            "suburb": "Pentagon",
                            "district": "Brussels",
                            "city": "City of Brussels",
                            "county": "Brussels-Capital",
                            "state": "Brussels-Capital",
                            "postcode": "1000",
                            "country": "Belgium",
                            "country_code": "be",
                            "lon": 4.3649087,
                            "lat": 50.8512746,
                            "distance": 0,
                            "result_type": "amenity",
                            "housenumber": 103,
                            "formatted": "Corinthia Grand Hôtel Astoria, Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium",
                            "address_line1": "Corinthia Grand Hôtel Astoria",
                            "address_line2": "Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium",
                            "category": "building",
                            "rank": {
                                "importance": 0.2533630197666373,
                                "popularity": 8.756741365970566,
                            },
                            "place_id": "517f1a52a0aa751140592f75eb90f66c4940f00101f901d2c52d000000000092031e436f72696e74686961204772616e642048c3b474656c204173746f726961",
                            "bbox": {
                                "lon1": 4.3647787,
                                "lat1": 50.8509602,
                                "lon2": 4.3655858,
                                "lat2": 50.8514369,
                            }
                        }
                    ]
                }
            }
        ]
    },
    {
        "api": "/v1/geocode/reverse",
        "params": {"format": "json"},
        "id": "f7c91d84a7004397898aef7af856b7c5",
        "results": [
            {
                "params": {"lat": 50.554534, "lon": 30.215443},
                "result": {
                    "results": [
                        {
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database License",
                                "url": "https://www.openstreetmap.org/copyright",
                            },
                            "name": "Продукти",
                            "street": "Nove Shose Street",
                            "city": "Bucha",
                            "district": "Bucansky district",
                            "state": "Kyiv Oblast",
                            "postcode": "08292",
                            "country": "Ukraine",
                            "country_code": "ua",
                            "lon": 30.215418995532495,
                            "lat": 50.55441705,
                            "distance": 7.500638769136665,
                            "result_type": "amenity",
                            "county": "Irpins'ka",
                            "formatted": "Продукти, Nove Shose Street, Bucansky district, Bucha, 08292, Ukraine",
                            "address_line1": "Продукти",
                            "address_line2": "Nove Shose Street, Bucansky district, Bucha, 08292, Ukraine",
                            "category": "commercial.convenience",
                            "rank": {"popularity": 8.677102176087054},
                            "place_id": "51cebf04b325373e4059220c4d23f7464940f00102f9013332eb1800000000920310d09fd180d0bed0b4d183d0bad182d0b8e203216f70656e7374726565746d61703a76656e75653a7761792f343138303636393935",
                            "bbox": {
                                "lon1": 30.2153296,
                                "lat1": 50.5543666,
                                "lon2": 30.2155084,
                                "lat2": 50.5544675,
                            }
                        }
                    ]
                }
            }
        ]
    }]

RES_TEST_BATCH_PLACES = [
{
    "api": "/v2/places",
    "params": {
        "format": "json",
        "categories": [
            "accommodation.hotel",
            "accommodation.hostel",
            "accommodation.motel",
        ],
        "limit": 3,
    },
    "id": "3b213d5b513644778aa72c73238378b5",
    "results": [
        {
            "params": {
                "filter": "rect:11.563106549898483,48.12898913611139,11.57704581350751,48.13666585409989",
                "conditions": "named",
            },
            "result": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Deutsche Eiche",
                            "housenumber": "13",
                            "street": "Reichenbachstraße",
                            "neighbourhood": "Gärtnerplatz",
                            "suburb": "Gärtnerplatz",
                            "district": "Ludwigsvorstadt-Isarvorstadt",
                            "city": "Munich",
                            "state": "Bavaria",
                            "postcode": "80469",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 11.576359869215747,
                            "lat": 48.132741550000006,
                            "formatted": "Deutsche Eiche, Reichenbachstraße 13, 80469 Munich, Germany",
                            "address_line1": "Deutsche Eiche",
                            "address_line2": "Reichenbachstraße 13, 80469 Munich, Germany",
                            "categories": [
                                "accommodation",
                                "accommodation.hotel",
                                "building",
                                "building.accommodation",
                                "wheelchair",
                                "wheelchair.limited",
                            ],
                            "details": [
                                "details",
                                "details.accommodation",
                                "details.building",
                                "details.contact",
                                "details.facilities",
                                "details.wiki_and_media",
                            ],
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database Licence",
                                "url": "https://www.openstreetmap.org/copyright",
                                "raw": {
                                    "name": "Deutsche Eiche",
                                    "lgbtq": "primary",
                                    "stars": "3S",
                                    "osm_id": 99876859,
                                    "tourism": "hotel",
                                    "website": "https://www.deutsche-eiche.com/",
                                    "building": "yes",
                                    "operator": "Josef Sattler GmbH",
                                    "osm_type": "w",
                                    "wikidata": "Q1630878",
                                    "addr:city": "München",
                                    "wikipedia": "de:Hotel Deutsche Eiche",
                                    "start_date": 1864,
                                    "wheelchair": "limited",
                                    "addr:street": "Reichenbachstraße",
                                    "contact:fax": " 49 89 23116698",
                                    "addr:country": "DE",
                                    "addr:postcode": 80469,
                                    "contact:email": "info@deutsche-eiche.com",
                                    "contact:phone": " 49 89 2311660",
                                    "addr:housenumber": 13,
                                },
                            },
                            "place_id": "51efd7d3a4182727405994dd03acfd104840f00102f901fbfff3050000000092030e4465757473636865204569636865",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [11.57635989271145, 48.13274145306346],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Hotel Atlanta",
                            "housenumber": "58",
                            "street": "Sendlinger Straße",
                            "quarter": "Hackenviertel",
                            "suburb": "Altstadt-Lehel",
                            "city": "Munich",
                            "state": "Bavaria",
                            "postcode": "80331",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 11.56825361565961,
                            "lat": 48.13447675,
                            "formatted": "Hotel Atlanta, Sendlinger Straße 58, 80331 Munich, Germany",
                            "address_line1": "Hotel Atlanta",
                            "address_line2": "Sendlinger Straße 58, 80331 Munich, Germany",
                            "categories": [
                                "accommodation",
                                "accommodation.hotel",
                                "building",
                                "building.accommodation",
                                "building.residential",
                                "internet_access",
                                "internet_access.free",
                            ],
                            "details": [
                                "details",
                                "details.accommodation",
                                "details.contact",
                                "details.facilities",
                            ],
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database Licence",
                                "url": "https://www.openstreetmap.org/copyright",
                                "raw": {
                                    "fax": " 49 89 2609027",
                                    "name": "Hotel Atlanta",
                                    "email": "info@hotel-atlanta.de",
                                    "phone": " 49 89 263605",
                                    "stars": 2,
                                    "osm_id": 55800408,
                                    "smoking": "no",
                                    "tourism": "hotel",
                                    "website": "http://www.hotel-atlanta.de/",
                                    "building": "apartments",
                                    "osm_type": "w",
                                    "addr:city": "München",
                                    "addr:street": "Sendlinger Straße",
                                    "addr:country": "DE",
                                    "addr:postcode": 80331,
                                    "internet_access": "wlan",
                                    "addr:housenumber": 58,
                                    "internet_access:fee": "no",
                                },
                            },
                            "place_id": "516b60c1d2ec22274059cc86883f37114840f00102f901587253030000000092030d486f74656c2041746c616e7461",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [11.56821306810908, 48.134498540557246],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude",
                            "housenumber": "18",
                            "street": "Kreuzstraße",
                            "quarter": "Hackenviertel",
                            "suburb": "Altstadt-Lehel",
                            "city": "Munich",
                            "state": "Bavaria",
                            "postcode": "80331",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 11.5675918,
                            "lat": 48.135158,
                            "formatted": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude, Kreuzstraße 18, 80331 Munich, Germany",
                            "address_line1": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude",
                            "address_line2": "Kreuzstraße 18, 80331 Munich, Germany",
                            "categories": [
                                "accommodation",
                                "accommodation.hotel",
                                "internet_access",
                            ],
                            "details": [
                                "details",
                                "details.accommodation",
                                "details.contact",
                                "details.facilities",
                            ],
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database Licence",
                                "url": "https://www.openstreetmap.org/copyright",
                                "raw": {
                                    "fax": " 49 89 23036701",
                                    "name": "Hotel Herzog Wilhelm Tannenbaum Nebengebäude",
                                    "email": "info@herzog-wilhelm.de",
                                    "phone": " 49 89 230360",
                                    "stars": 3,
                                    "osm_id": 305433531,
                                    "tourism": "hotel",
                                    "website": "http://www.herzog-wilhelm.de",
                                    "operator": "Herzog-Wilhelm-Restaurant-Tannenbaum GmbH",
                                    "osm_type": "n",
                                    "addr:city": "München",
                                    "addr:street": "Kreuzstraße",
                                    "addr:country": "DE",
                                    "addr:postcode": 80331,
                                    "internet_access": "wlan",
                                    "addr:housenumber": 18,
                                },
                            },
                            "place_id": "51a0f474649b2227405963b17adb4c114840f00103f901bb8b34120000000092032d486f74656c204865727a6f672057696c68656c6d2054616e6e656e6261756d204e6562656e676562c3a4756465",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [11.567591800000002, 48.13515799990525],
                        },
                    },
                ],
            },
        },
        {
            "params": {"filter": "circle:7.010232,51.450216,3000"},
            "result": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Atlantic Congress Hotel",
                            "housenumber": "3",
                            "street": "Messeplatz",
                            "suburb": "Rüttenscheid",
                            "district": "Stadtbezirk II",
                            "city": "Essen",
                            "state": "North Rhine-Westphalia",
                            "postcode": "45131",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 6.9988989633788234,
                            "lat": 51.4316226,
                            "formatted": "Atlantic Congress Hotel, Messeplatz 3, 45131 Essen, Germany",
                            "address_line1": "Atlantic Congress Hotel",
                            "address_line2": "Messeplatz 3, 45131 Essen, Germany",
                            "categories": [
                                "accommodation",
                                "accommodation.hotel",
                                "building",
                                "building.accommodation",
                                "building.commercial",
                                "building.office",
                                "wheelchair",
                                "wheelchair.yes",
                            ],
                            "details": [
                                "details",
                                "details.building",
                                "details.contact",
                                "details.facilities",
                            ],
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database Licence",
                                "url": "https://www.openstreetmap.org/copyright",
                                "raw": {
                                    "name": "Atlantic Congress Hotel",
                                    "email": "info@atlantic-essen.de",
                                    "phone": " 49 201 9 46 28-0",
                                    "osm_id": 37075109,
                                    "tourism": "hotel",
                                    "website": "https://www.atlantic-congress-hotel-messe-essen.de/gastronomie/",
                                    "building": "commercial",
                                    "osm_type": "w",
                                    "addr:city": "Essen",
                                    "wheelchair": "yes",
                                    "addr:street": "Messeplatz",
                                    "addr:country": "DE",
                                    "addr:postcode": 45131,
                                    "building:levels": 3,
                                    "addr:housenumber": 3,
                                },
                            },
                            "place_id": "511a4fc797defe1b4059fe3d0f653fb74940f00102f901a5b835020000000092031741746c616e74696320436f6e677265737320486f74656c",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [6.998895999469619, 51.4316221546578],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Hotel Boutique Essen City",
                            "housenumber": "19",
                            "street": "Hoffnungstraße",
                            "suburb": "Stadtkern",
                            "district": "Stadtbezirk I",
                            "city": "Essen",
                            "state": "North Rhine-Westphalia",
                            "postcode": "45127",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 7.006111000165929,
                            "lat": 51.4549952,
                            "formatted": "Hotel Boutique Essen City, Hoffnungstraße 19, 45127 Essen, Germany",
                            "address_line1": "Hotel Boutique Essen City",
                            "address_line2": "Hoffnungstraße 19, 45127 Essen, Germany",
                            "categories": [
                                "accommodation",
                                "accommodation.hotel",
                                "building",
                                "building.accommodation",
                            ],
                            "details": [
                                "details",
                                "details.building",
                                "details.contact",
                            ],
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database Licence",
                                "url": "https://www.openstreetmap.org/copyright",
                                "raw": {
                                    "name": "Hotel Boutique Essen City",
                                    "brand": "Trip Inn Hotels",
                                    "email": "boutique-essen@tripinn-hotels.com",
                                    "phone": " 49 201 22 14 14",
                                    "osm_id": 49319745,
                                    "tourism": "hotel",
                                    "website": "https://tripinn-hotels.com/essen-boutique/",
                                    "building": "yes",
                                    "osm_type": "w",
                                    "addr:city": "Essen",
                                    "roof:shape": "flat",
                                    "addr:street": "Hoffnungstraße",
                                    "roof:colour": "black",
                                    "addr:country": "DE",
                                    "addr:postcode": 45127,
                                    "roof:material": "tar_paper",
                                    "building:colour": "white",
                                    "building:levels": 4,
                                    "addr:housenumber": 19,
                                    "building:material": "plaster",
                                },
                            },
                            "place_id": "510772231c42061c4059f2b3e70d3dba4940f00102f901418ff00200000000920319486f74656c20426f75746971756520457373656e2043697479",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [7.00611156431524, 51.454988229881465],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Ibis",
                            "housenumber": "50",
                            "street": "Hollestraße",
                            "suburb": "Ostviertel",
                            "district": "Stadtbezirk I",
                            "city": "Essen",
                            "state": "North Rhine-Westphalia",
                            "postcode": "45127",
                            "country": "Germany",
                            "country_code": "de",
                            "lon": 7.018488078348117,
                            "lat": 51.452833850000005,
                            "formatted": "Ibis, Hollestraße 50, 45127 Essen, Germany",
                            "address_line1": "Ibis",
                            "address_line2": "Hollestraße 50, 45127 Essen, Germany",
                            "categories": [
                                "accommodation",
                                "accommodation.hotel",
                                "building",
                                "building.accommodation",
                            ],
                            "details": [
                                "details",
                                "details.accommodation",
                                "details.contact",
                            ],
                            "datasource": {
                                "sourcename": "openstreetmap",
                                "attribution": "© OpenStreetMap contributors",
                                "license": "Open Database Licence",
                                "url": "https://www.openstreetmap.org/copyright",
                                "raw": {
                                    "fax": " 49 201 2 428 600",
                                    "name": "Ibis",
                                    "brand": "Ibis",
                                    "email": "H1444@ACCOR.COM",
                                    "phone": " 49 201 24 280",
                                    "stars": 2,
                                    "osm_id": 54170279,
                                    "tourism": "hotel",
                                    "website": "http://www.ibis.com/de/hotel-1444-ibis-essen-hauptbahnhof/index.shtml",
                                    "building": "yes",
                                    "osm_type": "w",
                                    "addr:city": "Essen",
                                    "addr:street": "Hollestraße",
                                    "addr:country": "DE",
                                    "addr:postcode": 45127,
                                    "brand:wikidata": "Q920166",
                                    "brand:wikipedia": "en:Ibis (hotel)",
                                    "addr:housenumber": 50,
                                },
                            },
                            "place_id": "51a12f70f5f7121c405911259c5af6b94940f00102f901a7923a030000000092030449626973",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [7.0185240125391894, 51.452830625765394],
                        },
                    },
                ],
            },
        },
    ],
}
]

RES_TEST_BATCH_PLACE_DETAILS = [
    {
        "api": "/v2/place-details",
        "params": {"format": "json", "features": "details,building"},
        "id": "85e72da01b57473a9a409ddf67472439",
        "results": [
            {
                "params": {"lat": 51.450216, "lon": 7.010232},
                "result": {
                    "type": "FeatureCollection",
                    "features": [
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
                                "coordinates": [
                                    [7.0108501, 51.450249699],
                                    [7.0093601, 51.450052299],
                                ],
                            },
                        },
                        {
                            "type": "Feature",
                            "properties": {
                                "feature_type": "building",
                                "categories": [
                                    "building",
                                    "building.office",
                                    "office",
                                    "office.company",
                                ],
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
                                "wiki_and_media": {
                                    "wikidata": "Q474287",
                                    "wikipedia": "de:Schenker AG",
                                },
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
                    ],
                },
            },
            {
                "params": {"lat": 50.8512746, "lon": 4.3649087},
                "result": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {
                                "feature_type": "details",
                                "website": "https://www.corinthia.com/brussels/",
                                "description": "https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld",
                                "name": "Corinthia Grand Hôtel Astoria",
                                "wiki_and_media": {
                                    "wikidata": "Q649690",
                                    "wikipedia": "en:Hotel Astoria, Brussels",
                                },
                                "building": {"type": "construction"},
                                "categories": ["building"],
                                "datasource": {
                                    "sourcename": "openstreetmap",
                                    "attribution": "© OpenStreetMap contributors",
                                    "license": "Open Database Licence",
                                    "url": "https://www.openstreetmap.org/copyright",
                                    "raw": {
                                        "name": "Corinthia Grand Hôtel Astoria",
                                        "osm_id": -2999762,
                                        "website": "https://www.corinthia.com/brussels/",
                                        "building": "construction",
                                        "osm_type": "r",
                                        "wikidata": "Q649690",
                                        "wikipedia": "en:Hotel Astoria, Brussels",
                                        "description": "https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld",
                                        "opening_date": "2024-06-01",
                                        "proposed:tourism": "hotel",
                                    },
                                },
                                "street": "Rue Royale - Koningsstraat",
                                "city": "City of Brussels",
                                "county": "Brussels-Capital",
                                "state": "Brussels-Capital",
                                "postcode": "1000",
                                "country": "Belgium",
                                "country_code": "be",
                                "formatted": "Corinthia Grand Hôtel Astoria, Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium",
                                "address_line1": "Corinthia Grand Hôtel Astoria",
                                "address_line2": "Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium",
                                "lat": 50.851208150000005,
                                "lon": 4.3654038908803035,
                                "place_id": "5177d3b20af9751140590a9a9800f46c4940f00101f901d2c52d000000000092031e436f72696e74686961204772616e642048c3b474656c204173746f726961",
                            },
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [4.3647787, 50.851130099],
                                        [4.3649217, 50.851094499],
                                        [4.3649394, 50.851130799],
                                        [4.3649988, 50.851119199],
                                        [4.3649796, 50.851079999],
                                        [4.3651534, 50.851036699],
                                        [4.3651721, 50.851077699],
                                        [4.3652199, 50.851065799],
                                        [4.3652006, 50.851024899],
                                        [4.3652285, 50.851017999],
                                        [4.3652901, 50.851003699],
                                        [4.3653076, 50.850999299],
                                        [4.3653419, 50.850990399],
                                        [4.3653824, 50.850980099],
                                        [4.3654073, 50.850973899],
                                        [4.3654312, 50.850967499],
                                        [4.3654639, 50.850960199],
                                        [4.3654869, 50.850992299],
                                        [4.365563, 50.851098099],
                                        [4.3655807, 50.851124499],
                                        [4.3655598, 50.851186599],
                                        [4.3655858, 50.851190599],
                                        [4.3655713, 50.851233599],
                                        [4.3655242, 50.851225699],
                                        [4.3655116, 50.851226199],
                                        [4.365509, 50.851233599],
                                        [4.365518, 50.851231799],
                                        [4.365551, 50.851295699],
                                        [4.3655273, 50.851300599],
                                        [4.3655137, 50.851302599],
                                        [4.3653644, 50.851339299],
                                        [4.3653426, 50.851298399],
                                        [4.3652968, 50.851308299],
                                        [4.3653189, 50.851350399],
                                        [4.3652015, 50.851379499],
                                        [4.3651893, 50.851355599],
                                        [4.3651634, 50.851361399],
                                        [4.3651776, 50.851385899],
                                        [4.3651334, 50.851395799],
                                        [4.3651193, 50.851369099],
                                        [4.3651023, 50.851372899],
                                        [4.3650939, 50.851356599],
                                        [4.3650595, 50.851363299],
                                        [4.365081, 50.851406499],
                                        [4.3649381, 50.851436899],
                                        [4.3647787, 50.851130099],
                                    ],
                                    [
                                        [4.3650345, 50.851161199],
                                        [4.3651073, 50.851299499],
                                        [4.3651238, 50.851295999],
                                        [4.3651158, 50.851280099],
                                        [4.3652348, 50.851255299],
                                        [4.3652436, 50.851271899],
                                        [4.3652588, 50.851268899],
                                        [4.3651882, 50.851130099],
                                        [4.3650345, 50.851161199],
                                    ],
                                ],
                            },
                        },
                        {
                            "type": "Feature",
                            "properties": {
                                "feature_type": "building",
                                "categories": ["building"],
                                "datasource": {
                                    "sourcename": "openstreetmap",
                                    "attribution": "© OpenStreetMap contributors",
                                    "license": "Open Database Licence",
                                    "url": "https://www.openstreetmap.org/copyright",
                                    "raw": {
                                        "name": "Corinthia Grand Hôtel Astoria",
                                        "osm_id": -2999762,
                                        "website": "https://www.corinthia.com/brussels/",
                                        "building": "construction",
                                        "osm_type": "r",
                                        "wikidata": "Q649690",
                                        "wikipedia": "en:Hotel Astoria, Brussels",
                                        "description": "https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld",
                                        "opening_date": "2024-06-01",
                                        "proposed:tourism": "hotel",
                                    },
                                },
                                "street": "Rue Royale - Koningsstraat",
                                "city": "City of Brussels",
                                "county": "Brussels-Capital",
                                "state": "Brussels-Capital",
                                "postcode": "1000",
                                "country": "Belgium",
                                "country_code": "be",
                                "formatted": "Corinthia Grand Hôtel Astoria, Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium",
                                "address_line1": "Corinthia Grand Hôtel Astoria",
                                "address_line2": "Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium",
                                "lat": 50.851208150000005,
                                "lon": 4.3654038908803035,
                                "name": "Corinthia Grand Hôtel Astoria",
                                "website": "https://www.corinthia.com/brussels/",
                                "description": "https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld",
                                "wiki_and_media": {
                                    "wikidata": "Q649690",
                                    "wikipedia": "en:Hotel Astoria, Brussels",
                                },
                                "building": {"type": "construction"},
                                "area": 1635,
                                "place_id": "5177d3b20af9751140590a9a9800f46c4940f00101f901d2c52d000000000092031e436f72696e74686961204772616e642048c3b474656c204173746f726961",
                            },
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [4.3647787, 50.851130099],
                                        [4.3649217, 50.851094499],
                                        [4.3649394, 50.851130799],
                                        [4.3649988, 50.851119199],
                                        [4.3649796, 50.851079999],
                                        [4.3651534, 50.851036699],
                                        [4.3651721, 50.851077699],
                                        [4.3652199, 50.851065799],
                                        [4.3652006, 50.851024899],
                                        [4.3652285, 50.851017999],
                                        [4.3652901, 50.851003699],
                                        [4.3653076, 50.850999299],
                                        [4.3653419, 50.850990399],
                                        [4.3653824, 50.850980099],
                                        [4.3654073, 50.850973899],
                                        [4.3654312, 50.850967499],
                                        [4.3654639, 50.850960199],
                                        [4.3654869, 50.850992299],
                                        [4.365563, 50.851098099],
                                        [4.3655807, 50.851124499],
                                        [4.3655598, 50.851186599],
                                        [4.3655858, 50.851190599],
                                        [4.3655713, 50.851233599],
                                        [4.3655242, 50.851225699],
                                        [4.3655116, 50.851226199],
                                        [4.365509, 50.851233599],
                                        [4.365518, 50.851231799],
                                        [4.365551, 50.851295699],
                                        [4.3655273, 50.851300599],
                                        [4.3655137, 50.851302599],
                                        [4.3653644, 50.851339299],
                                        [4.3653426, 50.851298399],
                                        [4.3652968, 50.851308299],
                                        [4.3653189, 50.851350399],
                                        [4.3652015, 50.851379499],
                                        [4.3651893, 50.851355599],
                                        [4.3651634, 50.851361399],
                                        [4.3651776, 50.851385899],
                                        [4.3651334, 50.851395799],
                                        [4.3651193, 50.851369099],
                                        [4.3651023, 50.851372899],
                                        [4.3650939, 50.851356599],
                                        [4.3650595, 50.851363299],
                                        [4.365081, 50.851406499],
                                        [4.3649381, 50.851436899],
                                        [4.3647787, 50.851130099],
                                    ],
                                    [
                                        [4.3650345, 50.851161199],
                                        [4.3651073, 50.851299499],
                                        [4.3651238, 50.851295999],
                                        [4.3651158, 50.851280099],
                                        [4.3652348, 50.851255299],
                                        [4.3652436, 50.851271899],
                                        [4.3652588, 50.851268899],
                                        [4.3651882, 50.851130099],
                                        [4.3650345, 50.851161199],
                                    ]
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    },
    {
        "api": "/v2/place-details",
        "params": {"format": "json", "features": "details,building"},
        "id": "33314d05cb2d41a49a5db343313d3707",
        "results": [
            {
                "params": {"lat": 50.554534, "lon": 30.215443},
                "result": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {
                                "feature_type": "details",
                                "name": "Києво-Мироцька вулиця",
                                "name_international": {
                                    "en": "Kyyevo-Myrotska Street",
                                    "ru": "Киево-Мироцкая улица",
                                    "uk": "Києво-Мироцька вулиця",
                                },
                                "categories": ["highway", "highway.residential"],
                                "datasource": {
                                    "sourcename": "openstreetmap",
                                    "attribution": "© OpenStreetMap contributors",
                                    "license": "Open Database Licence",
                                    "url": "https://www.openstreetmap.org/copyright",
                                    "raw": {
                                        "name": "Києво-Мироцька вулиця",
                                        "osm_id": 794467117,
                                        "highway": "residential",
                                        "name:en": "Kyyevo-Myrotska Street",
                                        "name:ru": "Киево-Мироцкая улица",
                                        "name:uk": "Києво-Мироцька вулиця",
                                        "z_order": 330,
                                        "osm_type": "w",
                                    },
                                },
                                "street": "Kyyevo-Myrotska Street",
                                "city": "Bucha",
                                "state": "Kyiv Oblast",
                                "postcode": "08292",
                                "country": "Ukraine",
                                "country_code": "ua",
                                "formatted": "Києво-Мироцька вулиця, Kyyevo-Myrotska Street, Bucha, 08292, Ukraine",
                                "address_line1": "Києво-Мироцька вулиця",
                                "address_line2": "Kyyevo-Myrotska Street, Bucha, 08292, Ukraine",
                                "lat": 50.554548,
                                "lon": 30.2156379,
                                "place_id": "51fb7cc0a838373e405994f14532fb464940f00102f9012d9b5a2f00000000920328d09ad0b8d194d0b2d0be2dd09cd0b8d180d0bed186d18cd0bad0b020d0b2d183d0bbd0b8d186d18f",
                            },
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [30.2159417, 50.554517399],
                                    [30.2156379, 50.554547999],
                                    [30.2154749, 50.554564399],
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }]
