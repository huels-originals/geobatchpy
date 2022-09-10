import os

from geoapify.client import Client


class TestClient:
    API_KEY = os.environ['GEOAPIFY_KEY']  # add yours to your environment variables

    def test_geocode(self):
        client = Client(api_key=self.API_KEY)

        res = client.geocode(text='Hülser Markt 1, 47839 Krefeld')

        res2 = client.geocode(parameters={'name': 'DB Schenker', 'city': 'Essen', 'country': 'Germany'})

        assert res['features'][0]['properties']['suburb'] == 'Hüls'
        assert res2['features'][0]['properties']['street'] == 'Kruppstraße'

    def test_reverse_geocode(self):
        client = Client(api_key=self.API_KEY)

        res = client.reverse_geocode(latitude='51.450216', longitude='7.010232')

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
