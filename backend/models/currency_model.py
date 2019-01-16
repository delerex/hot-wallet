import abc
from typing import Dict

from bitcoin import *

from models.wallet_config import WalletConfig


class CurrencyModel(abc.ABC):

    def float_to_decimal(self, value) -> int:
        return int(value * 10 ** self.decimals)

    def decimals_to_float(self, value) -> float:
        return float(value / 10 ** self.decimals)

    @abc.abstractmethod
    def generate_xpub(self, root_seed) -> str:
        pass

    @abc.abstractmethod
    def get_priv_pub_addr(self, root_seed, n) -> (str, str, str):
        pass

    def sign_data(self, data, privkey):
        hash = sha256(data)
        signature = ecdsa_raw_sign(hash, privkey)
        return encode_sig(*signature)

    def verify_data(self, data, signature, pubkey):
        hash = sha256(data)
        return ecdsa_raw_verify(hash, decode_sig(signature), bip32_extract_key(pubkey))

    @property
    @abc.abstractmethod
    def decimals(self):
        pass

    @abc.abstractmethod
    def get_addr_from_pub(self, pubkey, address_number):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_balance(self, addr):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_xpub(self, wallet: WalletConfig) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_nonce(self, addr):
        pass

    @abc.abstractmethod
    def send_transactions(self, masterseed, outs: Dict[str, int], start, end):
        pass
