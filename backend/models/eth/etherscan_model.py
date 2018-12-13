from typing import Optional

import requests

from models.multitransactions import MultiTransactionClass
from models.network_type import NetworkType


class EtherScan:
    _MAIN_ENDPOINT = "https://api.etherscan.io/api"
    _ROPSTEN_ENDPOINT = "https://api-ropsten.etherscan.io/api"

    def __init__(self, network=NetworkType.MAIN):
        if network == NetworkType.MAIN:
            self._endpoint = self._MAIN_ENDPOINT
            self._chain_id = 1
        elif network == NetworkType.TESTNET:
            self._endpoint = self._ROPSTEN_ENDPOINT
            self._chain_id = 3


    def balances(self):
        res = {}
        for w in self.wallets:
            r = self.balance(w)
            res[w] = r
        return r

    def process_transaction(self, transaction):
        print(transaction)
        mt = MultiTransactionClass("ETH", transaction["hash"])
        mt.settime(transaction["timeStamp"])

        mt.add_in(transaction["from"],
                  int(transaction["value"]) + (int(transaction["gasPrice"]) * int(transaction["gasUsed"])))
        mt.add_out(transaction["to"], int(transaction["value"]))

        return mt.to_json()

    def transactions(self, wallet_id, skip=0, limit=50):
        res = []
        r = self.get_transactions(wallet_id, skip, limit)
        print(f"transactions response: {r}")
        for ct in r["result"]:
            if int(ct["isError"]) == 0:
                t = self.process_transaction(ct)
                res.append(t)
        return res

    def balance(self, wallet):
        params = {"module": "account", "action": "balance", "address": wallet, "tag": "latest"
                  }
        r = requests.get(self._endpoint, params)
        ret = r.json()["result"]
        return ret

    @property
    def chain_id(self):
        return self._chain_id

    @property
    def gas_price(self):
        params = {"module": "proxy", "action": "eth_gasPrice"
                  }
        r = requests.get(self._endpoint, params)
        ret = r.json()["result"]
        return int(ret, 16)

    def estimate_gas(self, to, gasPrice, gas):
        params = {"module": "proxy", "action": "eth_estimateGas", "to": to, "gasPrice": gasPrice, "gas": gas
                  }
        r = requests.get(self._endpoint, params)
        ret = r.json()["result"]
        return ret

    def get_transactions(self, wallet, skip=0, limit=50):
        params = {"module": "account", "action": "txlist", "address": wallet, "tag": "latest",
                  "startblock": 0, "endblock": 999999999, "sort": "asc"}
        r = requests.get(self._endpoint, params)
        txs = r.json()
        return txs

    def send_transaction(self, transaction) -> Optional[str]:
        params = {"module": "proxy", "action": "eth_sendRawTransaction", "hex": transaction}
        r = requests.get(self._endpoint, params)
        txs = r.json()
        if "status" in txs and txs["status"] == "0":
            print(f"send_transaction response: {txs}")
            return None
        return txs["result"]

    def get_nonce(self, wallet_id) -> int:
        outcount = 0
        transactions = self.transactions(wallet_id, limit=10000)
        for ethtx in transactions:
            for o in ethtx["ins"]:
                if o.get("wallet", None) == wallet_id:
                    outcount += 1
        return outcount
