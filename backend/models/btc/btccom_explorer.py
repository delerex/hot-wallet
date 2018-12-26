from typing import List, Optional

import requests

from models.btc.btc_service import BtcService
from models.btc.input_transaction import InputTransaction
from models.network_type import NetworkType


class BtcComExplorer(BtcService):

    def __init__(self, symbol, network_type: str):
        """
        Client for btc.com API. Be aware! Testnet may not work!
        :param symbol: str: one of "BTC" or "BCH"
        :param network_type: - look at NetworkType class.
        """
        self._network_type = network_type
        self._endpoint = self._get_endpoint(symbol, network_type)

    @staticmethod
    def _get_endpoint(symbol: str, network_type: str) -> str:
        # Warning! Testnet may not work
        if symbol == "BTC":
            if network_type == NetworkType.MAIN:
                endpoint = "https://chain.api.btc.com/v3/"
            else:
                endpoint = "https://tchain.api.btc.com/v3/"
        elif symbol == "BCH":
            if network_type == NetworkType.MAIN:
                endpoint = "https://bch-chain.api.btc.com/v3/"
            else:
                endpoint = "https://bch-tchain.api.btc.com/v3/"
        else:
            raise ValueError(f"Unsupported symbol: {symbol}")
        return endpoint

    def get_balance(self, address) -> Optional[int]:
        resp = requests.get(f"{self._endpoint}address/{address}",
                            allow_redirects=True)
        data = resp.json()
        if data["data"] is None:
            return 0
        return data["data"]["balance"]

    def get_input_transactions(self, address) -> List[InputTransaction]:
        pass

    def get_fee_rate(self) -> float:
        pass

    def send_transaction(self, tx_hash):
        pass
