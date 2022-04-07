import requests
import json

class TeaplixAPI(object):
    def __init__(self, token, api_url):
        self.token = token
        self.headers = { 'APIToken': str(token) }
        self.api_url = api_url

    def __str__(self):
        return self.token

    def post(self, data, url_method):
        r = requests.post(
            str(self.api_url) + str(url_method),
            data=json.dumps(data),
            headers=self.headers
        )

        return json.loads(r.content.decode("utf-8"))
