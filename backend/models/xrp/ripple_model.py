from models.currency_model import CurrencyModel
from models.wallet_config import WalletConfig
from models.xrp.ripple_jsonrpc import RippleJsonRpc


class RippleModel(CurrencyModel):

    def __init__(self, network_type):
        self.data_api = RippleJsonRpc(network_type)
        self.currency = "XRP"

    def generate_xpub(self, root_seed) -> str:
        pass

    def get_priv_pub_addr(self, root_seed, n) -> (str, str, str):
        pass

    @property
    def decimals(self):
        return 6

    def get_addr_from_pub(self, pubkey, address_number):
        pass

    def get_balance(self, addr):
        balance = self.data_api.get_balance(addr)
        return self.decimals_to_float(balance)

    def get_xpub(self, wallet: WalletConfig) -> str:
        pass

    def get_nonce(self, addr):
        pass

    def send_transactions(self, masterseed, outs, start, end):
        pass