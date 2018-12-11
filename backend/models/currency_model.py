import abc

from bitcoin import *

from models.wallet_config import WalletConfig


class CurrencyModel(abc.ABC):

    def float_to_decimal(self, value) -> int:
        return int(value * 10 ** self.decimals)

    def decimal_to_float(self, value) -> float:
        return float(value / 10 ** self.decimals)

    def get_priv_pub_addr(self, root_seed, n):
        mk = bip32_master_key(root_seed)
        xpriv = bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 2 ** 31), 2 ** 31), 0), n)
        priv = bip32_extract_key(xpriv)
        pub = bip32_privtopub(xpriv)

        addr = privtoaddr(priv)
        return priv, pub, addr

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
