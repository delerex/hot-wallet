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
from models.errors import ApiInsufficientFund, ApiUnexpectedError, OperationFailed
from models.eth.eth_transaction_distribution import EthTransactionDistribution
from models.eth.input_wallet import InputWallet
from models.eth.transaction_intent import TransactionIntent
from models.tron.tron_api_factory import TronApiFactory
from models.wallet import Wallet
from models.wallet_config import WalletConfig
from models.xrp.b58 import b2a_hashed_base58


class TronModel(CurrencyModel):

    def __init__(self, network_type):
        super().__init__("TRX")
        api_factory = TronApiFactory()
        self.data_api = api_factory.create(network_type)
        self._transaction_distribution = EthTransactionDistribution()
        # 195'
        self.coin_index = CoinTypes.get_index("TRX")

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
        print("trx._get_balance_raw", addr, result)
        return result

    def get_address(self, key: BIP32Node) -> str:
        address_wallet_hash160 = key.hash160()

        return b2a_hashed_base58(h2b("00") + address_wallet_hash160)

    def _get_input_wallets(self, seed, start, end) -> List[InputWallet]:
        wallets = []
        for i in range(start, end):
            in_priv, in_pub, in_addr = self.get_priv_pub_addr(seed, i)
            balance = int(self._get_balance_raw(in_addr))
            wallets.append(InputWallet(in_priv, in_pub, in_addr, balance))
        return wallets

    def send_transactions(self, wallet: Wallet, outs_percent: Dict[str, int], start, end):
        if isinstance(outs_percent, dict):
            outs_percent = [(key, value) for (key, value) in outs_percent.items()]
        input_wallets = self._get_input_wallets(wallet.seed, start, end)
        print(f"send_transactions, input_wallets:\n {input_wallets}")
        input_wallets = [w for w in input_wallets if w.balance > 0]
        tx_intents = self._transaction_distribution.get_transaction_intents(input_wallets,
                                                                            outs_percent)
        txs = []
        for intent in tx_intents:
            intent: TransactionIntent = intent
            in_wallet = intent.in_wallet
            amount = self.decimals_to_float(intent.amount)
            print("trx: create transaction from:", in_wallet.address,
                  "to:", intent.out_address,
                  "amount:", amount)
            try:
                create_tx = self.data_api.create_transaction(intent.out_address,
                                                             amount,
                                                             in_wallet.address)

                # offline sign
                self.data_api.tron.private_key = in_wallet.priv
                offline_sign = self.data_api.trx.sign(create_tx)

                response = self.data_api.send_transaction(offline_sign)
                print(response)
                if "code" in response and response["code"] == "CONTRACT_VALIDATE_ERROR":
                    raise OperationFailed(response["message"])
            except ValueError as e:
                raise ApiInsufficientFund(str(e))

            tx_hash = response["transaction"]["txID"]
            txs.append(tx_hash)

        return txs

    def get_nonce(self, addr):
        pass
