import datetime
from time import sleep
from typing import Optional

import requests


class Ethplorer:
    _MAIN_ENDPOINT = "http://api.ethplorer.io/"
    _API_KEY = "freekey"
    _REQ_LIMIT = 0.5

    def __init__(self, api_key=_API_KEY, req_limit=_REQ_LIMIT):
        self._endpoint = self._MAIN_ENDPOINT
        self._api_key = api_key
        self._req_limit = req_limit
        self._last_request = 0

    def _restrain_request(self):
        now = datetime.datetime.now().timestamp()
        if now - self._last_request < 1 / self._req_limit:
            sleep_time = 1 / self._req_limit - (now - self._last_request)
            print(f"Ethplorer: reached rate limit, waiting for {sleep_time}s")
            sleep(sleep_time)
        self._last_request = datetime.datetime.now().timestamp()

    def _get(self, path="", params=None):
        return self._request(method="GET", path=path, params=params)

    def _request(self, method="GET", path="", params=None):
        if params is None:
            params = {}
        params["apiKey"] = self._api_key
        url = f"{self._endpoint}{path}?apiKey={self._api_key}"
        self._restrain_request()
        r = requests.request(method=method, url=url, params=params)
        return r.json()

    def get_address_info(self, address):
        ret = self._get(f"getAddressInfo/{address}")
        return ret

    def balance(self, wallet, symbol="ETH") -> Optional[int]:
        addr_info = self.get_address_info(wallet)
        if symbol == "ETH":
            return addr_info["ETH"]["balance"]
        for token in addr_info["tokens"]:
            if token["tokenInfo"]["symbol"] == symbol:
                return token["balance"]
        return None
