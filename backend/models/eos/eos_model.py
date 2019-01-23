import hashlib
from typing import Dict

from pycoin.encoding.hexbytes import h2b
from pycoin.key.BIP32Node import BIP32Node

from models.btc.network_factory import NetworkFactory
from models.currency_model import CurrencyModel
from models.eos.eos import Eos
from models.eos.eos_rpc import EosRps
from models.errors import ApiInsufficientFund
from models.wallet_config import WalletConfig


class EosModel(CurrencyModel):

    def __init__(self, network_type):
        self.data_api = EosRps(network_type)
        self.currency = "EOS"

    def generate_xpub(self, root_seed) -> str:
        wif = Eos.seed_to_wif(root_seed[:32])
        privkey = Eos.priv_from_wif(wif)
        pubkey = Eos.priv_to_pub(privkey)
        return Eos.pub_to_string(pubkey)

    def get_priv_pub_addr(self, root_seed, n) -> (str, str, str):
        wif = Eos.seed_to_wif(root_seed)
        privkey = Eos.priv_from_wif(wif)
        pubkey = Eos.priv_to_pub(privkey)
        pub_wif = Eos.pub_to_string(pubkey)
        priv_wif = wif.decode()
        return priv_wif, pub_wif, pub_wif

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
        return balance

    def _get_balance_raw(self, addr):
        return self.data_api.get_balance(addr)

    def send_transactions(self, seed, outs_percent: Dict[str, int], start, end):
        pass

    def get_nonce(self, addr):
        pass
