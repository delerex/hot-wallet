from typing import Optional, List

import rlp
import rlp.utils
from bitcoin import *
from ethereum import utils as u, transactions
from two1.bitcoin import HDPrivateKey

from models.currency_model import CurrencyModel
from models.etherscan_model import EtherScan
from models.wallet_config import WalletConfig


class EthereumClass(CurrencyModel):
    headers = {
        "Host": "blockchain.info",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://blockchain.info/pushtx",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }

    def __init__(self, network_type):
        self._decimals = 18
        self.etherscan = EtherScan(network_type)

    @property
    def decimals(self):
        return self._decimals

    def eth_pubtoaddr(self, x, y):
        return u.checksum_encode(
            u.sha3(u.encode_int32(x) + u.encode_int32(y))[12:]).lower()

    def get_addr_from_pub(self, pubkey, address_number):
        pk_addrs = bip32_ckd(bip32_ckd(pubkey, 0), int(address_number))
        keyf = decode_pubkey(bip32_extract_key(pk_addrs))
        addr = self.eth_pubtoaddr(keyf[0], keyf[1])
        return u.checksum_encode(addr)

    def get_priv_pub_addr(self, root_seed, n):
        mk = bip32_master_key(root_seed)

        hasha = bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 60 + 2 ** 31), 2 ** 31), 0), n)
        pub = u.privtopub(hasha)
        priv = bip32_extract_key(hasha)
        addr = "0x" + u.encode_hex(u.privtoaddr(priv[:-2]))

        return priv[:-2], pub, addr

    def get_balance(self, addr):
        return self.decimal_to_float(int(self.etherscan.balance(addr)))

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.eth_xpub

    def get_nonce(self, addr):
        txs = self.etherscan.get_transactions(addr)
        return len(txs)

    def send_transactions(self, masterseed, outs) -> List[str]:
        in_priv, in_pub, in_addr = self.get_priv_pub_addr(masterseed, 0)
        gas_price = self.etherscan.gas_price
        estimated_gas = 21000
        txs = []
        for out_addr, proportion in outs.items():
            nonce = self.etherscan.get_nonce(in_addr)
            tx = transactions.Transaction(nonce=nonce,
                                          to=out_addr[2:],
                                          value=self.float_to_decimal(0.1),
                                          gasprice=gas_price,
                                          startgas=estimated_gas,
                                          data=b"")
            signed = tx.sign(in_priv, self.etherscan.chain_id)
            unencoded_tx = rlp.encode(signed)
            signed_tx = "0x" + unencoded_tx.hex()
            tx_hash = self.etherscan.send_transaction(signed_tx)
            txs.append(tx_hash)

        return txs

    def research_problem(self, masterseed):
        masterkey = HDPrivateKey
