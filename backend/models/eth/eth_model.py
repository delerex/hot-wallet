from typing import List, Dict

import rlp
import rlp.utils
from bitcoin import *
from ethereum import utils as u, transactions

from models.currency_model import CurrencyModel
from models.eth.eth_transaction_distribution import EthTransactionDistribution
from models.eth.web3api.web3api_factory import Web3ApiFactory
from models.explorers.etherscan_model import EtherScan
from models.eth.input_wallet import InputWallet
from models.eth.transaction_intent import TransactionIntent
from models.explorers.web3api_service import Web3ApiService
from models.wallet import Wallet
from models.wallet_config import WalletConfig


class EthereumClass(CurrencyModel):

    def __init__(self, network_type, currency="ETH", decimals=18, coin_index=60,
                 contract_address=None):
        super().__init__(currency)
        self._decimals = decimals
        self.etherscan = EtherScan(network_type)
        self.coin_index = coin_index
        self.contract_address = contract_address
        web3api_factory = Web3ApiFactory()
        self._web3api = web3api_factory.create(network_type)
        self._web3api_service = Web3ApiService(self._web3api)
        self._transaction_distribution = EthTransactionDistribution()

    @property
    def decimals(self):
        return self._decimals

    def eth_pubtoaddr(self, x, y):
        return u.checksum_encode(
            u.sha3(u.encode_int32(x) + u.encode_int32(y))[12:]).lower()

    def generate_xpub(self, root_seed) -> str:
        mk = bip32_master_key(root_seed)
        hasha = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), self.coin_index + 2 ** 31), 2 ** 31)
        xpub = bip32_privtopub(hasha)
        return xpub

    def get_addr_from_pub(self, pubkey, address_number, change=0):
        pk_addrs = bip32_ckd(bip32_ckd(pubkey, change), int(address_number))
        keyf = decode_pubkey(bip32_extract_key(pk_addrs))
        addr = self.eth_pubtoaddr(keyf[0], keyf[1])
        return u.checksum_encode(addr)

    def get_priv_pub_addr(self, root_seed, n, change=0):
        mk = bip32_master_key(root_seed)

        hasha = bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), self.coin_index + 2 ** 31), 2 ** 31), change), n)
        pub = u.privtopub(hasha)
        priv = bip32_extract_key(hasha)
        addr = u.checksum_encode("0x" + u.encode_hex(u.privtoaddr(priv[:-2])))

        return priv[:-2], pub, addr

    def get_balance(self, addr):
        return self.decimals_to_float(self.get_balance_raw(addr))

    def get_balance_raw(self, addr):
        if self.currency == "ETH":
            balance = int(self.etherscan.balance(addr))
        else:
            balance = self._web3api_service.get_balance(addr, self.contract_address)
        return balance

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs.get(self.currency)

    def get_nonce(self, addr):
        txs = self.etherscan.get_transactions(addr)
        return len(txs)

    def _get_input_wallets(self, seed, start, end) -> List[InputWallet]:
        wallets = []
        for i in range(start, end):
            in_priv, in_pub, in_addr = self.get_priv_pub_addr(seed, i)
            balance = int(self.get_balance_raw(in_addr))
            wallets.append(InputWallet(in_priv, in_pub, in_addr, balance))
        return wallets

    def _get_nonce_dict(self, wallets: List[InputWallet]) -> Dict[str, int]:
        nonce_dict = {}
        for w in wallets:
            if w.balance > 0:
                nonce_dict[w.address] = self._web3api.get_transaction_count(w.address)
        return nonce_dict

    def send_transactions(self, wallet: Wallet, outs_percent, start, end) -> List[str]:
        if isinstance(outs_percent, dict):
            outs_percent = [(key, value) for (key, value) in outs_percent.items()]
        input_wallets = self._get_input_wallets(wallet.seed, start, end)
        print(f"send_transactions, input_wallets:\n {input_wallets}")
        input_wallets = [w for w in input_wallets if w.balance > 0]
        tx_intents = self._transaction_distribution.get_transaction_intents(input_wallets,
                                                                            outs_percent)
        print(f"send_transactions:\n {tx_intents}")
        gas_price = self.etherscan.gas_price
        estimated_gas = 21000
        txs = []
        nonce_dict = self._get_nonce_dict(input_wallets)
        for intent in tx_intents:
            intent: TransactionIntent = intent
            in_wallet = intent.in_wallet
            tx = self.create_transaction(estimated_gas, gas_price, intent, nonce_dict)
            if tx is None:
                continue
            #TODO : Ethereum library issue with network ID
            if self.etherscan.chain_id == 1:
                signed = tx.sign(in_wallet.priv)
            else:
                signed = tx.sign(in_wallet.priv, self.etherscan.chain_id)
            unencoded_tx = rlp.encode(signed)
            signed_tx = "0x" + unencoded_tx.hex()
            tx_hash = self.etherscan.send_transaction(signed_tx)
            txs.append(tx_hash)
            nonce_dict[in_wallet.address] += 1

        return txs

    def create_transaction(self, estimated_gas, gas_price, intent, nonce_dict):
        in_wallet = intent.in_wallet
        nonce = nonce_dict[in_wallet.address]
        print(f"nonce: {nonce}")
        fee = gas_price * estimated_gas
        in_amount = intent.amount - fee
        if in_amount <= 0:
            print(f"Insufficient funds: required: {fee}, found: {intent.amount}")
            tx = None
        else:
            tx = transactions.Transaction(nonce=nonce,
                                          to=intent.out_address[2:],
                                          value=intent.amount - fee,
                                          gasprice=gas_price,
                                          startgas=estimated_gas,
                                          data=b"")
        return tx
