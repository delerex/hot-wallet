import requests
from models.network_type import NetworkType


class BlockchainInfo:

    def __init__(self, network_type: str):
        self._network_type = network_type
        if network_type == NetworkType.MAIN:
            self._endpoint = "https://api.blockcypher.com/v1/btc/main/"
        else:
            self._endpoint = "https://api.blockcypher.com/v1/btc/test3/"

    def get_balance(self, addr):
        resp = requests.get(f"{self._endpoint}addrs/{addr}/balance",
                            allow_redirects=True)
        data = resp.json()
        return data["balance"]
