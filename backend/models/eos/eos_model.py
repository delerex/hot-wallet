import hashlib
from typing import Dict

from models.currency_model import CurrencyModel
from models.eos.eos import Eos
from models.eos.eos_rpc import EosRps
from models.eos.eospy.keys import EOSKey
from models.errors import ApiInsufficientFund, ApiObjectNotFound
from models.wallet import Wallet
from models.wallet_config import WalletConfig


class EosModel(CurrencyModel):

    def __init__(self, network_type):
        super().__init__("EOS")
        self.data_api = EosRps(network_type)

    def generate_xpub(self, root_seed) -> str:
        wif = Eos.seed_to_wif(root_seed[:32])
        privkey = EOSKey(wif)
        return privkey.to_public()

    def get_priv_pub_addr(self, root_seed, n) -> (str, str, str):
        priv_wif = Eos.seed_to_wif(root_seed[:32])
        privkey = EOSKey(priv_wif)
        pubkey = privkey.to_public()
        return priv_wif, pubkey, pubkey

    def get_addr_from_pub(self, pubkey, address_number):
        return pubkey

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs.get("EOS")

    @property
    def decimals(self):
        return 4

    @staticmethod
    def generate_tag(seed, n) -> int:
        s = seed + str(n)
        return int(hashlib.sha1(s.encode()).hexdigest(), 16) % (2 ** 32)

    def get_balance(self, addr):
        balance = self._get_balance_raw(addr)
        return str(balance)

    def _get_balance_raw(self, addr):
        return self.data_api.get_balance(addr)

    def _create_transactions(self, source: str, outs_percent: Dict[str, int]):
        transactions = []
        balance = self._get_balance_raw(source)
        if balance == 0:
            raise ApiInsufficientFund()
        print("xrp._create_transactions, balance", balance)
        for out_address, percent in outs_percent.items():
            amount = int(balance * percent / 100)
            if amount > 0:
                transactions.append(dict(
                    address=out_address,
                    amount=amount,
                ))
        return transactions

    def send_transactions(self, wallet: Wallet, outs_percent: Dict[str, int], start, end):
        if "account_id" not in wallet.data:
            raise ApiObjectNotFound("Set account_id before send transaction")
        account = wallet.data["account_id"]
        priv_key, pub_key, addr = self.get_priv_pub_addr(wallet.seed, 0)
        txs = self._create_transactions(account, outs_percent)
        result = []
        for tx in txs:
            response = self.data_api.send_transaction(sender=account,
                                                      receiver=tx["address"],
                                                      value=tx["amount"],
                                                      key=priv_key)
            print("send_transaction response", response)
            result.append(response)
        return result

    def get_nonce(self, addr):
        pass
