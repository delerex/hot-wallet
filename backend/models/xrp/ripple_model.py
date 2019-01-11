from pycoin.encoding.hexbytes import h2b
from pycoin.key.BIP32Node import BIP32Node

from models.btc.btc_model import BitcoinClass
from models.btc.network_factory import NetworkFactory
from models.xrp.b58 import b2a_hashed_base58
from models.xrp.ripple_jsonrpc import RippleJsonRpc


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

    def get_balance(self, addr):
        balance = self.data_api.get_balance(addr)
        return self.decimals_to_float(balance)

    def get_address(self, key: BIP32Node) -> str:
        address_wallet_hash160 = key.hash160()
        return b2a_hashed_base58(h2b("00") + address_wallet_hash160)

    # def get_xpub(self, wallet: WalletConfig) -> str:
    #     pass
    #
    # def get_nonce(self, addr):
    #     pass
    #
    # def send_transactions(self, masterseed, outs, start, end):
    #     pass