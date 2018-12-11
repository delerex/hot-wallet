from bitcoin import *
from models.currency_model import CurrencyModel
import requests


class BitcoinClass(CurrencyModel):
    headers = {
        "Host": "blockchain.info",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://blockchain.info/pushtx",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }

    def __init__(self):
        self.decimals = 10

    def get_addr_from_pub(self, pubkey, address_number):
        pk_addrs = bip32_ckd(bip32_ckd(pubkey, 0), address_number)
        addr = pubtoaddr(bip32_extract_key(pk_addrs))
        return addr

    def pub_to_addr(self, pubkey):
        return pubtoaddr(bip32_extract_key(pubkey))

    def get_balance(self, addr):
        resp = requests.get(f"https://blockchain.info/q/addressbalance/{addr}",
                            allow_redirects=True)
        return self.decimal_to_float(int(resp.text))

    def sign_data(self, data, privkey):
        hash = sha256(data)
        signature = ecdsa_raw_sign(hash, privkey)
        return encode_sig(*signature)

    def verify_data(self, data, signature, pubkey):
        hash = sha256(data)
        return ecdsa_raw_verify(hash, decode_sig(signature), bip32_extract_key(pubkey))
