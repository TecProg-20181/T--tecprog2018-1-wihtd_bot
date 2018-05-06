import json
import requests
import time
import urllib
from Classes.token import Token

URL = Token().getBotoken()

class Initialize:

    def __init__(self):
        self.content = None
        self.url = None
        self.response = None
        self.js = None

    def get_url(self, url):
        self.response = requests.get(url)
        self.content = self.response.content.decode("utf8")
        return self.content

    def get_json_from_url(self, url):
        self.content = self.get_url(url)
        self.js = json.loads(self.content)
        return self.js

    def get_updates(self, offset=None):
        self.url = URL + "getUpdates?timeout=100"
        if offset:
            self.url += "&offset={}".format(offset)
        self.js = self.get_json_from_url(self.url)
        return self.js

    def send_message(self, text, chat_id, reply_markup=None):
        text = urllib.parse.quote_plus(text)
        self.url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        if reply_markup:
            self.url += "&reply_markup={}".format(reply_markup)
        self.get_url(self.url)
