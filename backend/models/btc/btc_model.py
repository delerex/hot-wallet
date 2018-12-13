from bitcoin import *

from models.btc.blockchain_info import BlockchainInfo
from models.currency_model import CurrencyModel
import requests

from models.network_type import NetworkType
from models.wallet_config import WalletConfig


class BitcoinClass(CurrencyModel):

    headers = {
        "Host": "blockchain.info",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://blockchain.info/pushtx",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }

    def __init__(self, network_type: str):
        self._decimals = 10
        self._blockchain_info = BlockchainInfo(network_type=network_type)
        if network_type == NetworkType.MAIN:
            self._network_vbytes = MAINNET_PRIVATE
            self._magic_bytes = 0
        else:
            self._network_vbytes = TESTNET_PRIVATE
            self._magic_bytes = int("6F", 16)

    @property
    def decimals(self):
        return self._decimals

    def get_addr_from_pub(self, pubkey, address_number):
        pk_addrs = bip32_ckd(bip32_ckd(pubkey, 0), address_number)
        addr = pubkey_to_address(bip32_extract_key(pk_addrs), self._magic_bytes)
        return addr

    def pub_to_addr(self, pubkey):
        return pubkey_to_address(bip32_extract_key(pubkey), self._magic_bytes)

    def get_balance(self, addr):
        # resp = requests.get(f"https://blockchain.info/q/addressbalance/{addr}",
        #                     allow_redirects=True)
        # return self.decimal_to_float(int(resp.text))
        return self.decimal_to_float(int(self._blockchain_info.get_balance(addr)))

    def get_priv_pub_addr(self, root_seed, n):
        mk = bip32_master_key(root_seed, self._network_vbytes)
        xpriv = bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 2 ** 31), 2 ** 31), 0), n)
        priv = bip32_extract_key(xpriv)
        pub = bip32_privtopub(xpriv)

        addr = privkey_to_address(priv, self._magic_bytes)
        return priv, pub, addr

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.btc_xpub

    def get_nonce(self, addr) -> str:
        raise NotImplementedError()

    def send_transactions(self, outs):
        raise NotImplementedError()