import hashlib
from typing import Dict

from pycoin.encoding.hexbytes import h2b
from pycoin.key.BIP32Node import BIP32Node

from models.btc.btc_model import BitcoinClass
from models.btc.network_factory import NetworkFactory
from models.xrp.b58 import b2a_hashed_base58
from models.xrp.ripple_jsonrpc import RippleJsonRpc
from models.xrp.serialize import serialize_object
from models.xrp.sign import sign_transaction


class RippleModel(BitcoinClass):

    def __init__(self, network_type):
        super().__init__(network_type, symbol="XRP")
        self.data_api = RippleJsonRpc(network_type)
        self.currency = "XRP"
        network_factory = NetworkFactory()
        self._network = network_factory.get_network(self.currency, network_type)

    @property
    def decimals(self):
        return 6

    @staticmethod
    def generate_tag(seed, n) -> int:
        s = seed + str(n)
        return int(hashlib.sha1(s.encode()).hexdigest(), 16) % (2 ** 32)

    def get_balance(self, addr):
        balance = self._get_balance_raw(addr)
        return self.decimals_to_float(balance)

    def _get_balance_raw(self, addr):
        return self.data_api.get_balance(addr)

    def get_address(self, key: BIP32Node) -> str:
        address_wallet_hash160 = key.hash160()
        return b2a_hashed_base58(h2b("00") + address_wallet_hash160)

    def get_address_from_seed(self, seed) -> str:
        BIP32 = self._network.ui._bip32node_class
        master_key = BIP32.from_master_secret(seed)
        return self.get_address(master_key)

    def _create_transactions(self, source: str, outs_percent: Dict[str, int], fee):
        transactions = []
        account_info = self.data_api.get_account_info(source)
        balance = account_info["account_data"]["Balance"]
        sequence = account_info["Sequence"]
        for out_address, percent in outs_percent.items():
            amount = balance * percent / 100 - fee
            if amount > 0:
                transactions.append(dict(
                    Account=source,
                    Amount=self.decimals_to_float(amount),
                    Destination=out_address,
                    TransactionType="Payment",
                    Fee=fee,
                    Sequence=sequence,
                ))
                sequence += 1
        return transactions

    def send_transactions(self, seed, outs_percent: Dict[str, int], start, end):
        priv, xpub, addr = self.get_priv_pub_addr(seed, 0)
        fee = self.data_api.get_fee()
        transactions = self._create_transactions(addr, outs_percent, fee)
        txs = []
        for tx in transactions:
            signed_tx = sign_transaction(tx, priv)
            tx_blob = serialize_object(signed_tx)
            tx = self.data_api.submit(tx_blob=tx_blob)
            txs.append(tx["tx_json"]["hash"])
        return txs

    def get_nonce(self, addr) -> str:
        pass

    # def get_xpub(self, wallet: WalletConfig) -> str:
    #     pass
    #
    # def get_nonce(self, addr):
    #     pass
    #
    # def send_transactions(self, masterseed, outs, start, end):
    #     pass