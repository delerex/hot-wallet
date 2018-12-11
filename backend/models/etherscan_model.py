from models.multitransactions import MultiTransactionClass
import requests


class EtherScan():
    def __init__(self):
        self.PUBLIC_URL = "https://api.etherscan.io/api"

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

    def transactions(self, wallet_id):
        res = []
        r = self.get_transactions(wallet_id)
        for ct in r["result"]:
            if int(ct["isError"]) == 0:
                t = self.process_transaction(ct)
                res.append(t)
        return res

    def balance(self, wallet):
        params = {"module": "account", "action": "balance", "address": wallet, "tag": "latest"
                  }
        r = requests.get(self.PUBLIC_URL, params)
        ret = r.json()["result"]
        return ret

    def gas_price(self):
        params = {"module": "proxy", "action": "eth_gasPrice"
                  }
        r = requests.get(self.PUBLIC_URL, params)
        ret = r.json()["result"]
        return ret

    def estimate_gas(self, to, gasPrice, gas):
        params = {"module": "proxy", "action": "eth_estimateGas", "to": to, "gasPrice": gasPrice, "gas": gas
                  }
        r = requests.get(self.PUBLIC_URL, params)
        ret = r.json()["result"]
        return ret

    def get_transactions(self, wallet, skip=0, limit=50):
        params = {"module": "account", "action": "txlist", "address": wallet, "tag": "latest",
                  "startblock": 0, "endblock": 999999999, "sort": "asc"}
        r = requests.get(self.PUBLIC_URL, params)
        txs = r.json()
        return txs

    def send_transaction(self, transaction):
        params = {"module": "proxy", "action": "eth_sendRawTransaction", "hex": transaction}
        r = requests.get(self.PUBLIC_URL, params)
        txs = r.json()
        return txs
