import json
from decimal import Decimal
from time import sleep
from typing import Optional, List

import requests
from pycoin.coins.bitcoin.Spendable import Spendable

from models.btc.btc_service import BtcService
from models.btc.input_transaction import InputTransaction
from models.errors import OperationFailed
from models.network_type import NetworkType
from models.utils.coin_decimals import CoinDecimals
from pycoin.encoding.hexbytes import b2h_rev, h2b, h2b_rev


class BlockExplorerCom(BtcService):

    def __init__(self):
        self._endpoint = "https://blockexplorer.com/api/"
        self._decimals = CoinDecimals.get_decimals("BCH")

    @staticmethod
    def _request(url) -> Optional[dict]:
        sleep(0.2)
        resp = requests.get(url, allow_redirects=True)
        while resp.status_code == 429:
            print("Too many requests. Waiting...")
            sleep(1)
            resp = requests.get(url, allow_redirects=True)
        if resp.status_code != 200:
            print(
                f"Error while performing request {url} with status code {resp.status_code}: "
                f"{resp.text}")
            return None
        data = resp.json(parse_float=Decimal)
        if data["status"] == "failed":
            error_data = data["data"]
            print(f"Error while getting balance: {error_data}")
            return None
        return data

    @staticmethod
    def _post_request(url, data) -> dict:
        sleep(0.2)
        resp = requests.post(url, json=data, allow_redirects=True)
        while resp.status_code == 429:
            print("Too many requests. Waiting...")
            sleep(1)
            resp = requests.post(url, json=data, allow_redirects=True)
        if resp.status_code != 200:
            raise OperationFailed(message=resp.text)
        result = resp.json()
        if result["status"] == "fail":
            raise OperationFailed(message=json.dumps(result["data"]))
        return result["data"]

    def get_balance(self, address) -> Optional[int]:
        data = self._request(f"{self._endpoint}addr/{address}/balance")
        if data is None:
            return 0

        unconfirmed_balance = data["data"]["unconfirmed_balance"]
        confirmed_balance = data["data"]["confirmed_balance"]
        return self._decimals_to_int(unconfirmed_balance) + self._decimals_to_int(confirmed_balance)

    def _decimals_to_int(self, value):
        return int(Decimal(value) * (pow(10, self._decimals)))

    def _parse_input_transaction(self, addr, transaction):
        # {"txid" : "aa0507f13ad23359cd61c7df06ce198872dd1e1db688a39a6b14460c1f97325c",
        #         "block_no" : 1448197,
        #         "confirmations" : 387,
        #         "time" : 1545048750,
        #         "incoming" : {
        #           "output_no" : 0,
        #           "value" : "0.08349330",
        #           "spent" : null,
        #           "inputs" : [
        #             {
        #               "input_no" : 0,
        #               "address" : "n2L94gG1L9WCA1JbrynNDp7VNtwXRi5LE2",
        #               "received_from" : {
        #                 "txid" : "c788a976daf37442299c62525fe2d69fd50aa0cbbad22c35ce2a0e68e24b3195",
        #                 "output_no" : 0
        #               }
        #             }
        #           ],
        #           "req_sigs" : 1,
        #           "script_asm" : "OP_DUP OP_HASH160 29aa1e9eeade48b8778f45af10a8e1d2c8adfb29 OP_EQUALVERIFY
        #                            OP_CHECKSIG",
        #           "script_hex" : "76a91429aa1e9eeade48b8778f45af10a8e1d2c8adfb2988ac"
        #         }
        return InputTransaction(
            address=addr,
            value=self._decimals_to_int(transaction["incoming"]["value"]),
            is_spent=False,
            output=transaction["txid"] + ":" + str(transaction["incoming"]["output_no"]),
            block_height=transaction["block_no"]
        )

    def get_input_transactions(self, address) -> List[InputTransaction]:
        txs = self.get_transactions(address)
        return [self._parse_input_transaction(address, tx) for tx in txs if self._is_unspent_tx(tx)]

    @staticmethod
    def _is_unspent_tx(tx: dict) -> bool:
        return "incoming" in tx \
               and tx["incoming"]["spent"] is None

    def get_transactions(self, address) -> Optional[list]:
        data = self._request(f"{self._endpoint}address/{self._network}/{address}")
        if data is None:
            return None
        return data["data"]["txs"]

    def get_network_info(self) -> dict:
        data = self._request(f"{self._endpoint}get_info/{self._network}")
        return data["data"]

    def get_block(self, block_index) -> dict:
        print(f"get_block: {block_index}")
        data = self._request(f"{self._endpoint}block/{self._network}/{block_index}")
        return data["data"]

    def get_fee_rate(self) -> float:
        network_info = self.get_network_info()
        last_block_index = network_info["blocks"]
        avg_block_fee = []
        for i in range(last_block_index - 10, last_block_index):
            block = self.get_block(i)
            block_fee = float(self._decimals_to_int(block["fee"]))
            avg_fee = block_fee / block["size"]
            avg_block_fee.append(avg_fee)
        return sum(avg_block_fee) / float(len(avg_block_fee))

    def send_transaction(self, tx_hash):
        data = {
            "tx_hex": tx_hash
        }
        result = self._post_request(f"{self._endpoint}send_tx/{self._network}", data=data)
        print("send_transaction", result)

    def spendables_for_address(self, address):
        """
        Return a list of Spendable objects for the
        given bitcoin address.
        """
        spendables = []
        r = self._request(f"{self._endpoint}get_tx_unspent/{self._network}/{address}")

        print(f"spendables_for_address: {r}")
        for u in r["data"]['txs']:
            coin_value = self._decimals_to_int(u['value'])
            script = h2b(u["script_hex"])
            previous_hash = h2b_rev(u["txid"])
            previous_index = u["output_no"]
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables


if __name__ == "__main__":
    explorer = BlockExplorerCom("BTC")
    print(explorer.get_balance("1GD6mMpZTDVPaCJdwNBSwsei965aaTHV9D"))
    print(explorer.get_fee_rate())
