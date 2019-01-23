import json
from decimal import Decimal
from typing import Optional

import requests

from models.network_type import NetworkType


class EosRps:

    JUNGLE_ENDPOINTS = [
        "http://jungle2.cryptolions.io:80",
        "https://jungle2.cryptolions.io:443",
        "https://jungle.eosio.cr:443",
        "https://api.jungle.alohaeos.com:443",
        "http://145.239.133.201:8888",
        "https://jungle.eosn.io:443",
        "http://18.223.252.15:8888",
        "http://49.236.137.37:8880",
        "http://jungle.eosmetal.io:18888",
        "http://jungle2-eos.blckchnd.com:8888",
        "http://88.99.193.44:8888",
        "http://bp4-d3.eos42.io:8888",
        "http://88.12.21.79:8888",
        "http://150.95.198.181:8888",
        "https://jungle.eosphere.io:443",
        "http://nivm.net:8888",
        "http://213.202.230.42:8888",
        "http://213.202.230.42:8888",
        "http://107.182.23.236:8888",
        "http://194.44.30.52:5888",
    ]

    MAIN_ENPOINTS = [
        "https://eos.greymass.com"
    ]

    def __init__(self, network):
        self._version = "v1"
        self._network = network

    def get_endpoint(self, n=0):
        if self._network == NetworkType.TESTNET:
            host = self.JUNGLE_ENDPOINTS[n]
        else:
            host = self.MAIN_ENPOINTS[n]
        return host + "/" + self._version + "/"

    def request(self, method: str, path: str,
                params: Optional[dict] = None,
                json_data: Optional[dict] = None) -> Optional[dict]:
        # TODO switch between endpoints if response is wrong
        if params is None:
            params = {}
        url = self.get_endpoint() + path
        response = requests.request(method, url, params=params, json=json_data)
        if response.status_code == 200:
            result = response.json()
        else:
            if json_data is None:
                payload = ""
            else:
                payload = json.dumps(json_data)
            print("EOS request", method, url, payload,
                  "failed:", response.status_code, response.text)
            result = None
        return result

    def get_chain_info(self) -> Optional[dict]:
        return self.request("POST", "chain/get_info")

    def get_account(self, account_id) -> Optional[dict]:
        querystring = {"account_name": account_id}
        return self.request("POST", "chain/get_account", json_data=querystring)

    def get_balance(self, account_id) -> Optional[Decimal]:
        querystring = {"account": account_id, "currency": "EOS", "code": "eosio.token"}
        response = self.request("POST", "chain/get_currency_balance", json_data=querystring)
        if response is None:
            return response
        balance = None
        for item in response:
            (value, currency) = item.split(" ")
            if currency == "EOS":
                balance = Decimal(value)
        return balance
