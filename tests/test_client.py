import os
import requests

from geoapify.client import Client


class TestClient:
    API_KEY = os.environ['GEOAPIFY_KEY']  # add yours to your environment variables

    def test_place_details(self, monkeypatch):
        class MockRequestsGet:
            def __init__(self, url, params, headers):
                pass

            @staticmethod
            def json():
                return {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'feature_type': 'details', 'description': 'Renovation pending - expected to be opened again by 2019', 'name': 'Hotel Astoria', 'wiki_and_media': {'wikidata': 'Q649690'}, 'categories': [], 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database Licence', 'url': 'https://www.openstreetmap.org/copyright', 'raw': {'name': 'Hotel Astoria', 'osm_id': 4851793010, 'osm_type': 'n', 'wikidata': 'Q649690', 'addr:city': 'Bruxelles - Brussel', 'addr:street': 'Rue Royale - Koningsstraat', 'description': 'Renovation pending - expected to be opened again by 2019', 'addr:country': 'BE', 'addr:postcode': 1000, 'disused:tourism': 'hotel', 'addr:housenumber': 103}}, 'housenumber': '103', 'street': 'Rue Royale - Koningsstraat', 'city': 'City of Brussels', 'county': 'Brussels-Capital', 'state': 'Brussels-Capital', 'postcode': '1000', 'country': 'Belgium', 'country_code': 'be', 'formatted': 'Hotel Astoria, Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium', 'address_line1': 'Hotel Astoria', 'address_line2': 'Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium', 'lat': 50.8512746, 'lon': 4.3649087, 'place_id': '517f1a52a0aa7511405923e7e990f66c4940f00103f901727c30210100000092030d486f74656c204173746f726961'}, 'geometry': {'type': 'Point', 'coordinates': [4.3649087, 50.851274599]}}]}
        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        place_id = '517f1a52a0aa751140592f75eb90f66c4940f00103f901727' \
                   'c302101000000c0020192030d486f74656c204173746f726961'
        res = client.place_details(place_id=place_id)

        monkeypatch.setattr(MockRequestsGet, 'json', lambda _: {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'feature_type': 'details', 'website': 'https://www.corinthia.com/brussels/', 'description': 'https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld', 'name': 'Corinthia Grand Hôtel Astoria', 'wiki_and_media': {'wikidata': 'Q649690', 'wikipedia': 'en:Hotel Astoria, Brussels'}, 'building': {'type': 'construction'}, 'categories': ['building'], 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database Licence', 'url': 'https://www.openstreetmap.org/copyright', 'raw': {'name': 'Corinthia Grand Hôtel Astoria', 'osm_id': -2999762, 'website': 'https://www.corinthia.com/brussels/', 'building': 'construction', 'osm_type': 'r', 'wikidata': 'Q649690', 'wikipedia': 'en:Hotel Astoria, Brussels', 'description': 'https://www.bruzz.be/videoreeks/dinsdag-9-februari-2021/video-prestigehotel-astoria-wordt-tegen-2024-ere-hersteld', 'opening_date': '2024-06-01', 'proposed:tourism': 'hotel'}}, 'street': 'Rue Royale - Koningsstraat', 'city': 'City of Brussels', 'county': 'Brussels-Capital', 'state': 'Brussels-Capital', 'postcode': '1000', 'country': 'Belgium', 'country_code': 'be', 'formatted': 'Corinthia Grand Hôtel Astoria, Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium', 'address_line1': 'Corinthia Grand Hôtel Astoria', 'address_line2': 'Rue Royale - Koningsstraat, 1000 City of Brussels, Belgium', 'lat': 50.851208150000005, 'lon': 4.3654038908803035, 'place_id': '5177d3b20af9751140590a9a9800f46c4940f00101f901d2c52d000000000092031e436f72696e74686961204772616e642048c3b474656c204173746f726961'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[4.3647787, 50.851130099], [4.3649217, 50.851094499], [4.3649394, 50.851130799], [4.3649988, 50.851119199], [4.3649796, 50.851079999], [4.3651534, 50.851036699], [4.3651721, 50.851077699], [4.3652199, 50.851065799], [4.3652006, 50.851024899], [4.3652285, 50.851017999], [4.3652901, 50.851003699], [4.3653076, 50.850999299], [4.3653419, 50.850990399], [4.3653824, 50.850980099], [4.3654073, 50.850973899], [4.3654312, 50.850967499], [4.3654639, 50.850960199], [4.3654869, 50.850992299], [4.365563, 50.851098099], [4.3655807, 50.851124499], [4.3655598, 50.851186599], [4.3655858, 50.851190599], [4.3655713, 50.851233599], [4.3655242, 50.851225699], [4.3655116, 50.851226199], [4.365509, 50.851233599], [4.365518, 50.851231799], [4.365551, 50.851295699], [4.3655273, 50.851300599], [4.3655137, 50.851302599], [4.3653644, 50.851339299], [4.3653426, 50.851298399], [4.3652968, 50.851308299], [4.3653189, 50.851350399], [4.3652015, 50.851379499], [4.3651893, 50.851355599], [4.3651634, 50.851361399], [4.3651776, 50.851385899], [4.3651334, 50.851395799], [4.3651193, 50.851369099], [4.3651023, 50.851372899], [4.3650939, 50.851356599], [4.3650595, 50.851363299], [4.365081, 50.851406499], [4.3649381, 50.851436899], [4.3647787, 50.851130099]], [[4.3650345, 50.851161199], [4.3651073, 50.851299499], [4.3651238, 50.851295999], [4.3651158, 50.851280099], [4.3652348, 50.851255299], [4.3652436, 50.851271899], [4.3652588, 50.851268899], [4.3651882, 50.851130099], [4.3650345, 50.851161199]]]}}]})

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
                return

        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        res = client.geocode(text='Botzweg 40a, 47839 Krefeld')

        # update monkey patch for second call
        monkeypatch.setattr(MockRequestsGet, 'json', lambda _: {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors','license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'},'name': 'DB Schenker', 'housenumber': '4', 'street': 'Kruppstraße', 'suburb': 'Sternviertel','district': 'Stadtbezirk I', 'city': 'Essen', 'state': 'North Rhine-Westphalia', 'postcode': '45128','country': 'Germany', 'country_code': 'de', 'lon': 7.010418352964237, 'lat': 51.4503917,'formatted': 'DB Schenker, Kruppstraße 4, 45128 Essen, Germany', 'address_line1': 'DB Schenker','address_line2': 'Kruppstraße 4, 45128 Essen, Germany', 'result_type': 'amenity','rank': {'importance': 0.7195218989809715, 'popularity': 8.464778201466588, 'confidence': 1,'confidence_city_level': 1, 'match_type': 'full_match'},'place_id': '51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb07710000000000c0020192030b444220536368656e6b6572'},'geometry': {'type': 'Point', 'coordinates': [7.010418352964237, 51.4503917]},'bbox': [7.0093446, 51.4501399, 7.0106896, 51.4506423]}, {'type': 'Feature', 'properties': {'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors','license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'},'name': 'DB Schenker', 'housenumber': '81', 'street': 'Alfredstraße', 'suburb': 'Rüttenscheid','district': 'Stadtbezirk II', 'city': 'Essen', 'state': 'North Rhine-Westphalia', 'postcode': '45130','country': 'Germany', 'country_code': 'de', 'lon': 7.002773, 'lat': 51.4346836,'formatted': 'DB Schenker, Alfredstraße 81, 45130 Essen, Germany', 'address_line1': 'DB Schenker','address_line2': 'Alfredstraße 81, 45130 Essen, Germany', 'result_type': 'amenity','rank': {'importance': 0.42099999999999993, 'popularity': 7.729958748897548, 'confidence': 1,'confidence_city_level': 1, 'match_type': 'full_match'},'place_id': '514b3fe1ecd6021c4059c40d53b6a3b74940f00103f901ba6be90501000000c0020192030b444220536368656e6b6572'},'geometry': {'type': 'Point','coordinates': [7.002773,51.4346836]},'bbox': [7.002723, 51.4346336, 7.002823,51.4347336]}], 'query': {'text': '','parsed': {'house': 'DB Schenker','city': 'Essen','country': 'Germany','expected_type': 'amenity'}}})

        res2 = client.geocode(parameters={'name': 'DB Schenker', 'city': 'Essen', 'country': 'Germany'})

        assert res['features'][0]['properties']['suburb'] == 'Hüls'
        assert res2['features'][0]['properties']['street'] == 'Kruppstraße'

    def test_reverse_geocode(self, monkeypatch):
        class MockRequestsGet:
            def __init__(self, url, params, headers):
                pass

            @staticmethod
            def json():
                return {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'name': 'DB Schenker', 'housenumber': '4', 'street': 'Kruppstraße', 'suburb': 'Sternviertel', 'district': 'Stadtbezirk I', 'city': 'Essen', 'state': 'North Rhine-Westphalia', 'postcode': '45128', 'country': 'Germany', 'country_code': 'de', 'lon': 7.010418352964237, 'lat': 51.4503917, 'distance': 2.09919434696081, 'result_type': 'amenity', 'county': 'Essen', 'formatted': 'DB Schenker, Kruppstraße 4, 45128 Essen, Germany', 'address_line1': 'DB Schenker', 'address_line2': 'Kruppstraße 4, 45128 Essen, Germany', 'rank': {'importance': 0.29952189898097165, 'popularity': 8.464778201466588}, 'place_id': '51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb0771000000000092030b444220536368656e6b6572e203246f70656e7374726565746d61703a76656e75653a72656c6174696f6e2f37343037353437'}, 'geometry': {'type': 'Point', 'coordinates': [7.010418352964237, 51.4503917]}, 'bbox': [7.0093446, 51.4501399, 7.0106896, 51.4506423]}]}

        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        res = client.reverse_geocode(latitude=51.450216, longitude=7.010232)

        assert res['features'][0]['properties']['name'] == 'DB Schenker'

    def test_batch_geocode(self, monkeypatch):
        class MockRequestsPost:
            def __init__(self, request_url, json, headers, params):
                pass

            @staticmethod
            def json():
                return {'url': ''}

        global content_ind
        content_ind = -1

        class MockRequestsGet:
            def __init__(self, url, headers):
                self.content = [[{'query': {'text': 'Botzweg 40A, 47839 Krefeld', 'parsed': {'housenumber': '40a', 'street': 'botzweg', 'postcode': '47839', 'city': 'krefeld', 'expected_type': 'building'}}, 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'housenumber': '40a', 'street': 'Botzweg', 'suburb': 'Hüls', 'city': 'Krefeld', 'state': 'Rhénanie-du-Nord-Westphalie', 'postcode': '47839', 'country': 'Allemagne', 'country_code': 'de', 'lon': 6.514218325709599, 'lat': 51.36440725, 'formatted': 'Botzweg 40a, 47839 Krefeld, Allemagne', 'address_line1': 'Botzweg 40a', 'address_line2': '47839 Krefeld, Allemagne', 'category': 'building', 'result_type': 'building', 'rank': {'importance': 0.21100000000000002, 'popularity': 5.409281326081194, 'confidence': 1, 'confidence_city_level': 1, 'confidence_street_level': 1, 'match_type': 'full_match'}, 'place_id': '51d8b4af3f8f0e1a4059709692e5a4ae4940f00102f9010df1001300000000c00203'}, {'query': {'text': 'DB Schenker, Essen, Germany', 'parsed': {'house': 'db schenker', 'city': 'essen', 'country': 'germany', 'expected_type': 'amenity'}}, 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'name': 'DB Schenker', 'housenumber': '4', 'street': 'Kruppstraße', 'suburb': 'Sternviertel', 'district': 'Stadtbezirk I', 'city': 'Essen', 'state': 'Rhénanie-du-Nord-Westphalie', 'postcode': '45128', 'country': 'Allemagne', 'country_code': 'de', 'lon': 7.010418352964237, 'lat': 51.4503917, 'formatted': 'DB Schenker, Kruppstraße 4, 45128 Essen, Allemagne', 'address_line1': 'DB Schenker', 'address_line2': 'Kruppstraße 4, 45128 Essen, Allemagne', 'result_type': 'amenity', 'rank': {'importance': 0.5995218989809716, 'popularity': 8.464778201466588, 'confidence': 1, 'confidence_city_level': 1, 'match_type': 'full_match'}, 'place_id': '51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb07710000000000c0020192030b444220536368656e6b6572'}], [{'query': {'text': 'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen', 'parsed': {'house': 'jci beteiligungs gmbh', 'housenumber': '5', 'street': 'am schimmersfeld', 'city': 'ratingen', 'expected_type': 'amenity'}}, 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'housenumber': '5', 'street': 'Am Schimmersfeld', 'suburb': 'Tiefenbroich', 'city': 'Ratingen', 'county': 'Kreis Mettmann', 'state': 'Rhénanie-du-Nord-Westphalie', 'postcode': '40880', 'country': 'Allemagne', 'country_code': 'de', 'lon': 6.8305828, 'lat': 51.3015775, 'formatted': 'Am Schimmersfeld 5, 40880 Ratingen, Allemagne', 'address_line1': 'Am Schimmersfeld 5', 'address_line2': '40880 Ratingen, Allemagne', 'result_type': 'building', 'rank': {'importance': 0.31100000000000005, 'popularity': 6.432032060963271, 'confidence': 0.9, 'confidence_city_level': 1, 'confidence_street_level': 1, 'match_type': 'match_by_building'}, 'place_id': '51fe7a2a4c84521b4059cfda6d179aa64940f00103f9015f2517b900000000c00203'}]]

            def json(self):
                global content_ind
                content_ind += 1
                return self.content[content_ind]

        monkeypatch.setattr(requests, 'post', MockRequestsPost)
        monkeypatch.setattr(requests, 'get', MockRequestsGet)

        client = Client(api_key=self.API_KEY)

        addresses = ['Botzweg 40A, 47839 Krefeld', 'DB Schenker, Essen, Germany',
                     'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

        res = client.batch_geocode(addresses=addresses, batch_len=2, parameters={'lang': 'fr'})

        assert len(res) == len(addresses)
        assert res[0]['housenumber'] == '40a'
        assert res[1]['city'] == 'Essen'
        assert res[2]['country'] == 'Allemagne'

    def test_batch_reverse_geocode(self, monkeypatch):
        class MockReqestsGet:
            def __init__(self):
                pass

            @staticmethod
            def json():
                return [{'query': {'lon': 7.010232, 'lat': 51.450216}, 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'name': 'DB Schenker', 'housenumber': '4', 'street': 'Kruppstraße', 'suburb': 'Sternviertel', 'district': 'Stadtbezirk I', 'city': 'Essen', 'state': 'North Rhine-Westphalia', 'postcode': '45128', 'country': 'Germany', 'country_code': 'de', 'lon': 7.010418352964237, 'lat': 51.4503917, 'distance': 2.09919434696081, 'result_type': 'amenity', 'county': 'Essen', 'formatted': 'DB Schenker, Kruppstraße 4, 45128 Essen, Germany', 'address_line1': 'DB Schenker', 'address_line2': 'Kruppstraße 4, 45128 Essen, Germany', 'rank': {'importance': 0.29952189898097165, 'popularity': 8.464778201466588}, 'place_id': '51d009d51bab0a1c4059e6f16a6fa6b94940f00101f901bb0771000000000092030b444220536368656e6b6572e203246f70656e7374726565746d61703a76656e75653a72656c6174696f6e2f37343037353437'}, {'query': {'lon': 4.3649087, 'lat': 50.8512746}, 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'name': 'Corinthia Grand Hôtel Astoria', 'street': 'Rue Royale - Koningsstraat', 'suburb': 'Pentagon', 'district': 'Brussels', 'city': 'City of Brussels', 'county': 'Brussels-Capital', 'state': 'Brussels-Capital', 'postcode': '1000', 'country': 'Belgium', 'country_code': 'be', 'lon': 4.3649087, 'lat': 50.8512746, 'distance': 0, 'result_type': 'amenity', 'housenumber': 103, 'formatted': 'Corinthia Grand Hôtel Astoria, Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium', 'address_line1': 'Corinthia Grand Hôtel Astoria', 'address_line2': 'Rue Royale - Koningsstraat 103, 1000 City of Brussels, Belgium', 'category': 'building', 'rank': {'importance': 0.2533630197666373, 'popularity': 8.756741365970566}, 'place_id': '517f1a52a0aa751140592f75eb90f66c4940f00101f901d2c52d000000000092031e436f72696e74686961204772616e642048c3b474656c204173746f726961'}, {'query': {'lon': 30.215443, 'lat': 50.554534}, 'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'name': 'Продукти', 'street': 'Nove Shose Street', 'city': 'Bucha', 'district': 'Bucansky district', 'state': 'Kyiv Oblast', 'postcode': '08292', 'country': 'Ukraine', 'country_code': 'ua', 'lon': 30.215418995532495, 'lat': 50.55441705, 'distance': 7.500638769136665, 'result_type': 'amenity', 'county': "Irpins'ka", 'formatted': 'Продукти, Nove Shose Street, Bucansky district, Bucha, 08292, Ukraine', 'address_line1': 'Продукти', 'address_line2': 'Nove Shose Street, Bucansky district, Bucha, 08292, Ukraine', 'category': 'commercial.convenience', 'rank': {'popularity': 8.677102176087054}, 'place_id': '51cebf04b325373e4059220c4d23f7464940f00102f9013332eb1800000000920310d09fd180d0bed0b4d183d0bad182d0b8e203216f70656e7374726565746d61703a76656e75653a7761792f343138303636393935'}]

        monkeypatch.setattr(requests, 'get', MockReqestsGet)

        client = Client(api_key=self.API_KEY)

        geocodes = [(7.010232, 51.450216), (4.3649087, 50.8512746), (30.215443, 50.554534)]

        res = client.batch_reverse_geocode(geocodes=geocodes, batch_len=2)

        assert len(res) == len(geocodes)
        assert res[0]['name'] == 'DB Schenker'
        assert res[1]['country'] == 'Belgium'
        assert res[2]['city'] == 'Bucha'
