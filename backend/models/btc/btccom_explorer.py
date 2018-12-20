from typing import List, Optional

import requests

from models.btc.btc_service import BtcService
from models.btc.input_transaction import InputTransaction
from models.network_type import NetworkType


class BtcComExplorer(BtcService):

    def __init__(self, network_type: str):
        self._network_type = network_type
        if network_type == NetworkType.MAIN:
            self._endpoint = "https://chain.api.btc.com/v3/"
        else:
            self._endpoint = "https://tchain.api.btc.com/v3/"

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
