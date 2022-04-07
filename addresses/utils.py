import requests
import json

class SmartyStreetsAPI(object):
    def __init__(self):
        self.headers = { "referer": "http://unitedworldlogistics.com/" }
        self.api_url = "https://us-autocomplete-pro.api.smartystreets.com/lookup?"

    def __str__(self):
        return self.token

    def get(self, search, selected=None):
        payload = {
            "key": "7321538415709905",
            "search": search,
        }
        if selected:
            payload['selected'] = selected

        r = requests.get(
            self.api_url,
            params=payload,
            headers=self.headers,
        )

        return json.loads(r.content.decode("utf-8"))


