import os

from geoapify.client import Client


class TestClient:
    API_KEY = os.environ['GEOAPIFY_KEY']  # add yours to your environment variables

    def test_place_details(self):
        client = Client(api_key=self.API_KEY)

        place_id = '517f1a52a0aa751140592f75eb90f66c4940f00103f901727' \
                   'c302101000000c0020192030d486f74656c204173746f726961'
        res = client.place_details(place_id=place_id)

        lat, lon = 50.8512746, 4.3649087
        res2 = client.place_details(latitude=lat, longitude=lon)

        assert res['features'][0]['properties']['street'] == res2['features'][0]['properties']['street']

    def test_geocode(self):
        client = Client(api_key=self.API_KEY)

        res = client.geocode(text='Hülser Markt 1, 47839 Krefeld')

        res2 = client.geocode(parameters={'name': 'DB Schenker', 'city': 'Essen', 'country': 'Germany'})

        assert res['features'][0]['properties']['suburb'] == 'Hüls'
        assert res2['features'][0]['properties']['street'] == 'Kruppstraße'

    def test_reverse_geocode(self):
        client = Client(api_key=self.API_KEY)

        res = client.reverse_geocode(latitude=51.450216, longitude=7.010232)

        assert res['features'][0]['properties']['name'] == 'DB Schenker'

    def test_batch_geocode(self):
        client = Client(api_key=self.API_KEY)

        addresses = ['Hülser Markt 1, 47839 Krefeld', 'DB Schenker, Essen, Germany',
                     'JCI Beteiligungs GmbH, Am Schimmersfeld 5, Ratingen']

        res = client.batch_geocode(addresses=addresses, batch_len=2, parameters={'lang': 'fr'})

        assert len(res) == len(addresses)
        assert res[0]['housenumber'] == '1'
        assert res[1]['city'] == 'Essen'
        assert res[2]['country'] == 'Allemagne'

    def test_batch_reverse_geocode(self):
        client = Client(api_key=self.API_KEY)

        geocodes = [(7.010232, 51.450216), (4.3649087, 50.8512746), (30.215443, 50.554534)]

        res = client.batch_reverse_geocode(geocodes=geocodes, batch_len=2)

        assert len(res) == len(geocodes)
        assert res[0]['name'] == 'DB Schenker'
        assert res[1]['country'] == 'Belgium'
        assert res[2]['city'] == 'Bucha'
