from bitcoin import *
from models.currency_model import CurrencyModel
import requests
from ethereum import utils as u
from ethereum import transactions as tr
from models.multitransactions import multitransactionclass
import requests
from models.etherscan_model import EtherScan
from Crypto.Hash import keccak, SHA3_256


class EthereumClass(CurrencyModel):
    headers = {
        "Host": "blockchain.info",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://blockchain.info/pushtx",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }

    def __init__(self):
        self.decimals = 18
        self.etherscan = EtherScan()

    def eth_pubtoaddr(self, x, y):
        return u.checksum_encode(
            u.sha3(u.encode_int32(x) + u.encode_int32(y))[12:]).lower()

    def get_addr_from_pub(self, pubkey, address_number):
        pk_addrs = bip32_ckd(bip32_ckd(pubkey, 0), int(address_number))
        keyf = decode_pubkey( bip32_extract_key(pk_addrs))
        addr = self.eth_pubtoaddr(keyf[0], keyf[1])
        return u.checksum_encode(addr)


    def get_balance(self, addr):
        return int(self.etherscan.balance(addr))



