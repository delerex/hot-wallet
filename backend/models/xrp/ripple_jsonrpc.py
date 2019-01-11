from typing import Optional

import requests

from models.network_type import NetworkType


class RippleJsonRpc:

    def __init__(self, network_type):
        if network_type == NetworkType.MAIN:
            self._endpoint = "https://s1.ripple.com:51234/"
        elif network_type == NetworkType.TESTNET:
            self._endpoint = "https://s.altnet.rippletest.net:51234"

    def _request(self, method, params=None):
        headers = {'content-type': 'application/json'}

        if params is None:
            params = {}

        # Example echo method
        payload = {
            "method": method,
            "params": [params],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(self._endpoint, json=payload, headers=headers)
        if response.status_code != 200:
            print(response.text)
            return None
        result = response.json()
        return result

    def get_balance(self, address: str) -> Optional[int]:
        response = self._request("account_info", params={
            "account": address
        })
        print("get_balance response", response)
        if response is None:
            return None
        if response["result"]["status"] == "error":
            print(("get_balance error for ", address, response["result"]))
            return 0
        return int(response["result"]["account_data"]["Balance"])
