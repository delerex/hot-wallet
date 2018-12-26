from decimal import Decimal
from time import sleep
from typing import List, Optional

import requests
from pycoin.coins.bitcoin.Spendable import Spendable
from pycoin.encoding.hexbytes import h2b_rev

from models.explorers.btc_service import BtcService
from models.btc.input_transaction import InputTransaction
from models.btc.network_factory import NetworkFactory
from models.network_type import NetworkType
from models.utils.coin_decimals import CoinDecimals


class BtcComExplorer(BtcService):
    _ENDPOINTS = {
        "BTC": {
            NetworkType.MAIN: "https://chain.api.btc.com/",
            NetworkType.TESTNET: "https://tchain.api.btc.com/",
        },
        "BCH": {
            NetworkType.MAIN: "https://bch-chain.api.btc.com/",
            NetworkType.TESTNET: "https://bch-tchain.api.btc.com/",
        },
    }

    _VERSION = 3

    def __init__(self, symbol, network_type: str):
        """
        Client for btc.com API. Be aware! Testnet may not work!
        Docs:
        https://btc.com/api-doc
        https://dev.btc.com/docs
        :param symbol: str: one of "BTC" or "BCH"
        :param network_type: - look at NetworkType class.
        """
        self._network_type = network_type
        self._endpoint = self._get_endpoint(symbol, network_type)
        network_factory = NetworkFactory()
        self._network = network_factory.get_network(symbol, network_type)
        self._decimals = CoinDecimals.get_decimals(symbol)

    def _get_endpoint(self, symbol: str, network_type: str) -> str:
        # Warning! Testnet may not work
        if symbol not in self._ENDPOINTS:
            raise ValueError(f"Unsupported symbol {symbol}")
        if network_type not in self._ENDPOINTS[symbol]:
            raise ValueError(f"Unsupported network type: {network_type}, for symbol {symbol}")
        return self._ENDPOINTS[symbol][network_type] + f"v{self._VERSION}/"

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
        print(f"data of request: {data}")
        if data["err_no"] != 0:
            error_data = data["err_msg"]
            print(f"Error request to btc.com: {error_data}")
            return None
        return data

    def get_balance(self, address) -> Optional[int]:
        resp = requests.get(f"{self._endpoint}address/{address}",
                            allow_redirects=True)
        data = resp.json()
        if data["data"] is None:
            return 0
        return data["data"]["balance"]

    def get_input_transactions(self, address) -> List[InputTransaction]:
        pass

    def get_block(self, block_index) -> dict:
        print(f"get_block: {block_index}")
        data = self._request(f"{self._endpoint}block/{block_index}")
        return data["data"]

    def get_fee_rate(self) -> float:
        latest = self.get_block("latest")
        last_block_index = latest["height"]
        avg_block_fee = []
        for i in range(last_block_index - 10, last_block_index):
            block = self.get_block(i)
            block_fee = float(block["reward_fees"])
            avg_fee = block_fee / block["size"]
            avg_block_fee.append(avg_fee)
        return sum(avg_block_fee) / float(len(avg_block_fee))

    def send_transaction(self, tx_hash):
        pass

    def get_unspent_tx(self, address) -> List[dict]:
        r = self._request(f"{self._endpoint}address/{address}/unspent")

        return r["data"]["list"]

    def get_transactions(self, address) -> List[dict]:
        r = self._request(f"{self._endpoint}address/{address}/tx")
        return r["data"]["list"]

    def get_spendables_for_address(self, address) -> List[Spendable]:
        """
        Return a list of Spendable objects for the
        given bitcoin address. It needs to create transaction via pycoin library.
        """
        unspent = self.get_unspent_tx(address)
        spendables = []
        r = self._request(f"{self._endpoint}address/{address}/unspent")

        print(f"spendables_for_address: {r}")

        for utx in unspent:
            coin_value = utx["value"]
            script = self._network.ui.script_for_address(address)
            previous_hash = h2b_rev(utx["tx_hash"])
            previous_index = utx["tx_output_n"]
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables
