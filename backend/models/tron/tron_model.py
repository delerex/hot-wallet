from typing import Dict

import base58
from bitcoin import *
from eth_keys.datatypes import PublicKey
from ethereum import utils as u
from pycoin.encoding.b58 import b2a_hashed_base58
from pycoin.encoding.hexbytes import h2b
from pycoin.key.BIP32Node import BIP32Node

from models.btc.network_factory import NetworkFactory
from models.currency_model import CurrencyModel
from models.errors import ApiInsufficientFund
from models.tron.tron_api_factory import TronApiFactory
from models.wallet import Wallet
from models.wallet_config import WalletConfig
from models.xrp.b58 import b2a_hashed_base58
from models.xrp.ripple import Ripple
from models.xrp.serialize import serialize_object
from models.xrp.sign import sign_transaction


class TronModel(CurrencyModel):

    def __init__(self, network_type, coin_index=60):
        super().__init__("TRX")
        api_factory = TronApiFactory()
        self.data_api = api_factory.create(network_type)
        self.coin_index = coin_index

    def eth_pubtoaddr(self, x, y):
        return u.checksum_encode(
            u.sha3(u.encode_int32(x) + u.encode_int32(y))[12:]).lower()

    def generate_xpub(self, root_seed) -> str:
        mk = bip32_master_key(root_seed)
        hasha = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), self.coin_index + 2 ** 31),
                          2 ** 31)
        xpub = bip32_privtopub(hasha)
        return xpub

    def get_addr_from_pub(self, pubkey, address_number, change=0):
        pk_addrs = bip32_ckd(bip32_ckd(pubkey, change), int(address_number))
        keyf = decode_pubkey(bip32_extract_key(pk_addrs))
        print(keyf)
        return self.address_from_pub_key(keyf)

    def get_priv_pub_addr(self, root_seed, n, change=0):
        mk = bip32_master_key(root_seed)

        hasha = bip32_ckd(bip32_ckd(
            bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), self.coin_index + 2 ** 31), 2 ** 31),
            change), n)
        print("hasha", hasha)
        pub = u.privtopub(hasha)
        priv = bip32_extract_key(hasha)
        trx_addr = self.address_from_pub_key(pub)

        return priv[:-2], pub, trx_addr

    def address_from_pub_key(self, keyf):
        x, y = keyf
        pub_hex = u.encode_int32(x) + u.encode_int32(y)
        pub_key = PublicKey(pub_hex)
        address = '41' + pub_key.to_address()[2:]
        to_base58 = base58.b58encode_check(bytes.fromhex(address))
        address_base58 = to_base58.decode()
        return address_base58

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs["TRX"]

    @property
    def decimals(self):
        return 6

    def get_balance(self, addr):
        balance = self._get_balance_raw(addr)
        return self.decimals_to_float(balance)

    def _get_balance_raw(self, addr):
        return self.data_api.get_balance(addr)

    def get_address(self, key: BIP32Node) -> str:
        address_wallet_hash160 = key.hash160()

        return b2a_hashed_base58(h2b("00") + address_wallet_hash160)

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
