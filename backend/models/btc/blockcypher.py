from typing import List

import requests

from models.btc.btc_service import BtcService
from models.btc.input_transaction import InputTransaction
from models.network_type import NetworkType


class Blockcypher(BtcService):

    def __init__(self, network_type: str):
        self._network_type = network_type
        if network_type == NetworkType.MAIN:
            self._endpoint = "https://api.blockcypher.com/v1/btc/main/"
        else:
            self._endpoint = "https://api.blockcypher.com/v1/btc/test3/"

    @staticmethod
    def process_transaction(addr, transaction) -> InputTransaction:
        # {
        #     "tx_hash": "4c51f6228019a1619449d5f4b46bf95111d27b7599e340f848d485fb1ec61297",
        #     "block_height": 553734,
        #     "tx_input_n": -1,
        #     "tx_output_n": 0,
        #     "value": 2776564,
        #     "ref_balance": 2776564,
        #     "spent": false,
        #     "confirmations": 30,
        #     "confirmed": "2018-12-14T03:23:40Z",
        #     "double_spend": false
        #   },

        #   |
        #   V

        # {
        #     "address": "12vimHE11zzkYGTxtmws1kJiW5MV3FhBMh",
        #     "value": 1391504,
        #     "output": "3977a3e9bf55d1ea45fc9fda209f4b6d0c61c483a5315f9d84cdb0c3c2a0b139:0",
        #     "block_height": 551133,
        #     "spend": "d17f333598c6d4dafb794ac70d255e0828baa242e2b85c7fa3834b5eadca34b6:0"
        #   },
        return InputTransaction(
            address=addr,
            value=transaction["value"],
            is_spent=transaction.get("spent", True),
            output=transaction["tx_hash"] + ":" + str(transaction["tx_output_n"]),
            block_height=transaction["block_height"]
        )

    def get_blockchain(self):
        resp = requests.get(f"{self._endpoint}",
                            allow_redirects=True)
        data = resp.json()
        return data

    def get_fee_rate(self) -> float:
        blockchain = self.get_blockchain()
        fee_rate = blockchain["medium_fee_per_kb"] / 1000
        return fee_rate

    def get_balance(self, addr) -> int:
        resp = requests.get(f"{self._endpoint}addrs/{addr}/balance",
                            allow_redirects=True)
        data = resp.json()
        return data["balance"]

    def get_input_transactions(self, addr) -> List[InputTransaction]:
        txs = self.get_transactions(addr)
        return [self.process_transaction(addr, tx) for tx in txs if "spent" in tx]

    def get_transactions(self, addr):
        resp = requests.get(f"{self._endpoint}addrs/{addr}",
                            allow_redirects=True)
        data = resp.json()
        print(f"get_transactions: {data}")
        if data["n_tx"] == 0:
            return []
        return data["txrefs"]

    def send_transaction(self, tx_hash):
        data = {
            "tx": tx_hash
        }
        resp = requests.post(f"{self._endpoint}txs/push", json=data,
                             allow_redirects=True)
        result = resp.json()
        print("send_transaction", resp, result)
