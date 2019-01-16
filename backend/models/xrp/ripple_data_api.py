from decimal import Decimal

import requests

from models.network_type import NetworkType


class RippleDataApi:

    def __init__(self, network=NetworkType.MAIN):
        if network == NetworkType.MAIN:
            self._endpoint = "https://data.ripple.com/v2/"
        elif network == NetworkType.TESTNET:
            self._endpoint = "https://s.altnet.rippletest.net:51233/v2/"

    def _request(self, method="GET", path="", params=None):
        if params is None:
            params = {}
        url = f"{self._endpoint}{path}"
        # self._restrain_request()
        r = requests.request(method=method, url=url, params=params)
        print(r.text)
        return r.json()

    def get_balance(self, address: str, currency="XRP") -> int:
        path = f"accounts/{address}/balances"
        params = {}
        if currency is not None:
            params["currency"] = currency
        response = self._request(path=path, params=params)
        print(response)
        balance = Decimal(0)
        for data in response["balances"]:
            if data["currency"] == currency:
                balance += Decimal(data["value"])
        return balance
