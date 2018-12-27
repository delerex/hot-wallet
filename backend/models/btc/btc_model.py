from typing import List

from bitcoin import *
from pycoin.encoding.bytes32 import to_bytes_32
from pycoin.encoding.hexbytes import b2h
from pycoin.key.BIP32Node import BIP32Node
from pycoin.ui.key_from_text import key_from_text

from models.btc.network_factory import NetworkFactory
from models.explorers.btc_service import BtcService
from models.explorers.chain_so_explorer import ChainSoExplorer
from models.btc.input_transaction import InputTransaction
from models.currency_model import CurrencyModel
from models.network_type import NetworkType
from models.wallet_config import WalletConfig


class BitcoinClass(CurrencyModel):
    headers = {
        "Host": "blockchain.info",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://blockchain.info/pushtx",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }

    def __init__(self, network_type: str, symbol: str = "BTC"):
        self._decimals = 10
        # self._service: BtcService = Blockcypher(network_type=network_type)
        # self._service: BtcService = BtcComExplorer(network_type=network_type)
        self._service: BtcService = ChainSoExplorer.from_symbol_and_network_type("BTC",
                                                                                 network_type)
        network_factory = NetworkFactory()
        self._network = network_factory.get_network(symbol, network_type)
        if network_type == NetworkType.MAIN:
            self._network_vbytes = MAINNET_PRIVATE
            self._magic_bytes = 0
        else:
            self._network_vbytes = TESTNET_PRIVATE
            self._magic_bytes = int("6F", 16)

    @property
    def decimals(self):
        return self._decimals

    def get_addr_from_pub(self, account_xpub, address_number):
        account_key = key_from_text(account_xpub, networks=[self._network])
        address_key = account_key.subkey_for_path(f"0/{address_number}")
        return address_key.address()

    def pub_to_addr(self, pubkey):
        return pubkey_to_address(bip32_extract_key(pubkey), self._magic_bytes)

    def get_balance(self, addr):
        return self.decimals_to_float(int(self._service.get_balance(addr)))

    def generate_xpub(self, root_seed) -> str:
        BIP32Node = self._network.ui._bip32node_class
        master_key = BIP32Node.from_master_secret(root_seed)
        account_key = master_key.subkey_for_path("44p/0p/0p")
        account_xpub = account_key.as_text()
        return account_xpub

    def get_priv_pub_addr(self, root_seed, n):
        BIP32 = self._network.ui._bip32node_class
        master_key = BIP32.from_master_secret(root_seed)
        address_key: BIP32Node = master_key.subkey_for_path(f"44p/0p/0p/0/{n}")
        xpub = address_key.hwif(as_private=False)
        priv = b2h(to_bytes_32(address_key.secret_exponent()))
        addr = address_key.address(use_uncompressed=False)
        return priv, xpub, addr

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs.get("BTC")

    def get_nonce(self, addr) -> str:
        raise NotImplementedError()

    def _get_input_transactions(self, seed, start, end) -> List[InputTransaction]:
        input_transactions = []
        for i in range(start, end):
            in_priv, in_pub, in_addr = self.get_priv_pub_addr(seed, i)
            txs = self._service.get_input_transactions(in_addr)
            for tx in txs:
                if not tx.is_spent:
                    tx.priv_key = in_priv
                    input_transactions.append(tx)
        return input_transactions

    def send_transactions(self, seed, outs_percent, start, end):

        input_transactions = self._get_input_transactions(seed, start, end)
        balance = 0
        for tx in input_transactions:
            if not tx.is_spent:
                balance += tx.value
        print(f"balance: {balance}")
        if balance > 0:
            ins = [tx.to_dict() for tx in input_transactions]
            priv_keys = [tx.priv_key for tx in input_transactions]
            outs = [{"value": int(balance * percent / 100), "address": addr}
                    for (addr, percent) in outs_percent.items()]

            tx = self._generate_transaction(ins, outs, priv_keys)

            fee_rate = self._service.get_fee_rate()

            fee = int(fee_rate * len(tx) / 2)
            print(f"fee: {fee}")
            for item in outs:
                value = item["value"]
                item["value"] = value - int(fee * value / balance)

            print(f"outs: {outs}")

            tx = self._generate_transaction(ins, outs, priv_keys)

            print(f"generated tx: {tx}")

            self._service.send_transaction(tx)

    @staticmethod
    def _generate_transaction(ins, outs, priv_keys: list):
        tx = mktx(ins, outs)

        tx_signed = sign(tx, 0, priv_keys[0])
        if len(ins) > 1:
            for q in range(1, len(ins)):
                tx_signed = sign(tx_signed, q, priv_keys[q])

        trhash = txhash(tx_signed)
        return tx_signed
