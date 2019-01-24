import hashlib
from typing import Dict

from pycoin.encoding.hexbytes import h2b
from pycoin.key.BIP32Node import BIP32Node

from models.btc.network_factory import NetworkFactory
from models.currency_model import CurrencyModel
from models.errors import ApiInsufficientFund
from models.wallet import Wallet
from models.wallet_config import WalletConfig
from models.xrp.b58 import b2a_hashed_base58
from models.xrp.ripple import Ripple
from models.xrp.ripple_jsonrpc import RippleJsonRpc
from models.xrp.serialize import serialize_object
from models.xrp.sign import sign_transaction


class RippleModel(CurrencyModel):

    def __init__(self, network_type):
        super().__init__("XRP")
        self.data_api = RippleJsonRpc(network_type)
        network_factory = NetworkFactory()
        self._network = network_factory.get_network(self.currency, network_type)

    def generate_xpub(self, root_seed) -> str:
        return Ripple.pubkey_from_seed(root_seed)

    def get_priv_pub_addr(self, root_seed, n) -> (str, str, str):
        privkey = Ripple.privkey_from_seed(root_seed)
        pubkey = Ripple.pubkey_from_seed(root_seed)
        address = Ripple.address_from_seed(root_seed)
        return privkey, pubkey, address

    def get_addr_from_pub(self, pubkey, address_number):
        return Ripple.address_from_pubkey(pubkey)

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs.get("XRP")

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
        balance = int(account_info["Balance"])
        blocked_balance = self.get_blocked_balance()
        if balance <= self.get_blocked_balance():
            balance_ui = self.decimals_to_float(balance)
            balance_blocked_ui = self.decimals_to_float(blocked_balance)
            raise ApiInsufficientFund(f"Balance {balance_ui}, but for transaction required more "
                                      f"than {balance_blocked_ui}")
        balance -= blocked_balance
        sequence = account_info["Sequence"]
        print("xrp._create_transactions, balance", balance)
        for out_address, percent in outs_percent.items():
            amount = int(balance * percent / 100 - fee)
            if amount > 0:
                transactions.append(dict(
                    Account=source,
                    Amount=str(amount),
                    Destination=out_address,
                    TransactionType="Payment",
                    Fee=fee,
                    Sequence=sequence,
                ))
                sequence += 1
        return transactions

    def get_blocked_balance(self):
        return self.float_to_decimal(20)

    def send_transactions(self, wallet: Wallet, outs_percent: Dict[str, int], start, end):
        priv, xpub, addr = self.get_priv_pub_addr(wallet.seed, 0)
        secret = Ripple.secret_from_seed(wallet.seed)
        fee = self.data_api.get_fee()
        transactions = self._create_transactions(addr, outs_percent, fee)
        txs = []
        for tx in transactions:
            print("xrp transaction", tx)
            signed_tx = sign_transaction(tx, secret)
            tx_blob = serialize_object(signed_tx)
            tx = self.data_api.submit(tx_blob=tx_blob)
            print("xrp tx sent with response", tx)
            txs.append(tx["tx_json"]["hash"])
        return txs

    def get_nonce(self, addr):
        pass
