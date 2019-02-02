import json
from typing import Dict, List

import base58
from bitcoin import *
from eth_keys.datatypes import PublicKey
from ethereum import utils as u
from pycoin.encoding.b58 import b2a_hashed_base58
from pycoin.encoding.hexbytes import h2b
from pycoin.key.BIP32Node import BIP32Node
from tronapi.base.account import PrivateKey

from models.asset.coin_types import CoinTypes
from models.currency_model import CurrencyModel
from models.errors import ApiInsufficientFund, OperationFailed
from models.tron.input_wallet import InputWallet
from models.tron.output_wallet import OutputWallet
from models.tron.transaction_intent import TransactionIntent
from models.tron.tron_api_factory import TronApiFactory
from models.tron.trx_transaction_distribution import TronTransactionDistribution
from models.wallet import Wallet
from models.wallet_config import WalletConfig
from models.xrp.b58 import b2a_hashed_base58


class TronModel(CurrencyModel):

    def __init__(self, network_type):
        super().__init__("TRX")
        api_factory = TronApiFactory()
        self.data_api = api_factory.create(network_type)
        # 195'
        self.coin_index = CoinTypes.get_index("TRX")
        self._fee_net_usage = 268
        self._fee_new_account = 0.1
        self._tx_distribution = TronTransactionDistribution()

    def eth_pubtoaddr(self, x, y):
        return u.checksum_encode(
            u.sha3(u.encode_int32(x) + u.encode_int32(y))[12:]).lower()

    def generate_xpub(self, root_seed) -> str:
        mk = bip32_master_key(root_seed)
        hasha = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), self.coin_index + 2 ** 31),
                          2 ** 31)
        xpub = bip32_privtopub(hasha)
        return xpub

    def get_addr_from_pub(self, xpub, address_number, change=0):
        pk_addrs = bip32_ckd(bip32_ckd(xpub, change), int(address_number))
        keyf = decode_pubkey(bip32_extract_key(pk_addrs))
        x, y = keyf
        pub_hex = u.encode_int32(x) + u.encode_int32(y)

        return self.address_from_pub_key(pub_hex)

    def get_priv_pub_addr(self, root_seed, n, change=0):
        mk = bip32_master_key(root_seed)

        hasha = bip32_ckd(bip32_ckd(
            bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), self.coin_index + 2 ** 31), 2 ** 31),
            change), n)
        priv = bip32_extract_key(hasha)
        priv_key = PrivateKey(priv[:-2])
        pub = privkey_to_pubkey(priv)

        trx_addr = priv_key.address["base58"]

        return priv[:-2], pub[2:], trx_addr

    def address_from_pub_key(self, pub_hex):
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
        result = self.data_api.get_balance(addr)
        # print("trx._get_balance_raw", addr, result)
        return result

    def get_address(self, key: BIP32Node) -> str:
        address_wallet_hash160 = key.hash160()

        return b2a_hashed_base58(h2b("00") + address_wallet_hash160)

    def _get_input_wallets(self, seed, start, end) -> List[InputWallet]:
        wallets = []
        for i in range(start, end):
            in_priv, in_pub, in_addr = self.get_priv_pub_addr(seed, i)
            account = self.data_api.get_account(in_addr)
            # get actual balance if account exist else 0
            balance = account.get("balance", 0)
            resources = self.data_api.get_account_resource(in_addr)
            available_bandwidth = resources.get("freeNetLimit", 0) - resources.get("free_net_usage", 0)
            wallets.append(InputWallet(in_priv, in_pub, in_addr, balance, available_bandwidth))
        return wallets

    def _get_output_wallets(self, out_percent: Dict[str, int]) -> List[OutputWallet]:
        wallets = []
        for addr, percentage in out_percent.items():
            account = self.data_api.get_account(addr)
            is_exist = len(account) > 0
            wallets.append(OutputWallet(addr, is_exist, percentage))
        return wallets

    def send_transactions(self, wallet: Wallet, outs_percent: Dict[str, int], start, end):
        # if isinstance(outs_percent, dict):
        #     outs_percent = [(key, value) for (key, value) in outs_percent.items()]
        input_wallets = self._get_input_wallets(wallet.seed, start, end)
        output_wallets = self._get_output_wallets(outs_percent)
        # print(f"send_transactions, input_wallets:\n {input_wallets}")
        input_wallets = [w for w in input_wallets if w.balance > 0]

        tx_intents = self._tx_distribution.get_transaction_intents(input_wallets, output_wallets)
        print("trx: transaction intents:")
        for intent in tx_intents:
            print(intent)
        txs = []
        for intent in tx_intents:
            intent: TransactionIntent = intent
            in_wallet = intent.in_wallet
            amount = self.decimals_to_float(intent.amount)
            response = self._send_transaction(amount, in_wallet, intent.out_wallet.address)

            tx_hash = response["transaction"]["txID"]
            txs.append(tx_hash)

        return txs

    def _send_transaction(self, amount: float, in_wallet: InputWallet, out_address: str):
        print("trx: create transaction from:", in_wallet.address,
              "to:", out_address,
              "amount:", amount)
        try:
            created_tx = self.data_api.create_transaction(out_address,
                                                          amount,
                                                          in_wallet.address)
            # print("created_tx", created_tx)
            # offline sign
            self.data_api.tron.private_key = in_wallet.priv
            offline_sign = self.data_api.trx.sign(created_tx)

            response = self.data_api.send_transaction(offline_sign)
            print(response)
            if "code" in response and response["code"] == "CONTRACT_VALIDATE_ERROR":
                raise OperationFailed(response["message"])
        except ValueError as e:
            raise ApiInsufficientFund(str(e))
        return response

    def get_nonce(self, addr):
        pass
