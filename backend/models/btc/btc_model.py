import io
from typing import List, Tuple

from bitcoin import *
from pycoin.coins.bitcoin.Spendable import Spendable
from pycoin.coins.tx_utils import create_tx, sign_tx
from pycoin.encoding.bytes32 import to_bytes_32
from pycoin.encoding.hexbytes import b2h, h2b_rev
from pycoin.key.BIP32Node import BIP32Node
from pycoin.ui.key_from_text import key_from_text

from models.btc.network_factory import NetworkFactory
from models.asset.coin_types import CoinTypes
from models.explorers.btc_service import BtcService
from models.explorers.chain_so_explorer import ChainSoExplorer
from models.btc.input_transaction import InputTransaction
from models.currency_model import CurrencyModel
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

    def __init__(self, network_type: str, symbol: str = "BTC", explorer: BtcService = None):
        self._decimals = 10
        # self._service: BtcService = Blockcypher(network_type=network_type)
        # self._service: BtcService = BtcComExplorer(network_type=network_type)
        if explorer is None:
            explorer = ChainSoExplorer.from_symbol_and_network_type("BTC", network_type)
        self._service = explorer
        network_factory = NetworkFactory()
        self._network = network_factory.get_network(symbol, network_type)
        self._symbol = symbol
        self._currency_number = int(CoinTypes.get(symbol) - int(2 ** 31))

    @property
    def decimals(self):
        return self._decimals

    def get_addr_from_pub(self, account_xpub, address_number):
        account_key = key_from_text(account_xpub, networks=[self._network])
        address_key = account_key.subkey_for_path(f"0/{address_number}")
        return address_key.address()

    def get_balance(self, addr):
        return self.decimals_to_float(int(self._service.get_balance(addr)))

    def generate_xpub(self, root_seed) -> str:
        BIP32Node = self._network.ui._bip32node_class
        master_key = BIP32Node.from_master_secret(root_seed)
        account_key = master_key.subkey_for_path(f"44p/{self._currency_number}p/0p")
        account_xpub = account_key.as_text()
        return account_xpub

    def get_priv_pub_addr(self, root_seed, n):
        address_key: BIP32Node = self._get_priv_key(root_seed, n)
        xpub = self._get_xpub(address_key)
        priv = self._get_priv(address_key)
        addr = self._get_address(address_key)
        return priv, xpub, addr

    def _get_priv_key(self, root_seed, n) -> BIP32Node:
        BIP32 = self._network.ui._bip32node_class
        master_key = BIP32.from_master_secret(root_seed)
        path = f"44p/{self._currency_number}p/0p/0/{n}"
        address_key: BIP32Node = master_key.subkey_for_path(path)
        return address_key

    def _get_xpub(self, key: BIP32Node) -> str:
        return key.hwif(as_private=False)

    def _get_priv(self, key: BIP32Node) -> str:
        return b2h(to_bytes_32(key.secret_exponent()))

    def _get_address(self, key: BIP32Node) -> str:
        return key.address(use_uncompressed=False)

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs.get(self._symbol)

    def get_nonce(self, addr) -> str:
        raise NotImplementedError()

    def _get_input_transactions(self, seed, start, end) -> List[InputTransaction]:
        input_transactions = []
        for i in range(start, end):
            priv_key = self._get_priv_key(seed, i)
            in_addr = self._get_address(priv_key)
            txs = self._service.get_input_transactions(in_addr)
            for tx in txs:
                if not tx.is_spent:
                    tx.priv_key = priv_key
                    input_transactions.append(tx)
        return input_transactions

    def _input_tx_to_spendable(self, tx: InputTransaction) -> Spendable:
        outs = tx.output.split(":")
        tx_hash = h2b_rev(outs[0])
        output_n = int(outs[1])
        return Spendable(
            coin_value=tx.value,
            script=self._network.ui.script_for_address(tx.address),
            tx_hash=tx_hash,
            tx_out_index=output_n
        )

    def _input_txs_to_spendable(self, txs: List[InputTransaction]) -> List[Spendable]:
        return [self._input_tx_to_spendable(tx) for tx in txs]

    def send_transactions(self, seed, outs_percent, start, end):

        input_transactions = self._get_input_transactions(seed, start, end)
        balance = 0
        for tx in input_transactions:
            if not tx.is_spent:
                balance += tx.value
        print(f"balance: {balance}")
        if balance > 0:
            outs = [{"value": int(balance * percent / 100), "address": addr}
                    for (addr, percent) in outs_percent.items()]

            spendables = self._input_txs_to_spendable(input_transactions)
            payables = [(item["address"], item["value"]) for item in outs]

            tx = self._generate_transaction(spendables, input_transactions, payables)

            fee_rate = self._service.get_fee_rate()

            fee = int(fee_rate * len(tx) / 2)
            print(f"fee: {fee}")
            for item in outs:
                value = item["value"]
                item["value"] = value - int(fee * value / balance)

            print(f"outs: {outs}")

            payables = [(item["address"], item["value"]) for item in outs]
            tx = self._generate_transaction(spendables, input_transactions, payables)

            print(f"generated tx: {tx}")

            self._service.send_transaction(tx)

    def _generate_transaction(self,
                              spendables: List[Spendable],
                              ins: List[InputTransaction],
                              payables: List[Tuple]):
        tx = create_tx(spendables, payables, network=self._network, fee=0)

        priv_key = ins[0].priv_key
        sign_tx(tx, [priv_key.wif(False), priv_key.wif(True)],
                network=self._network)
        if len(ins) > 1:
            for q in range(1, len(ins)):
                priv_key = ins[q].priv_key
                sign_tx(tx, [priv_key.wif(False), priv_key.wif(True)],
                        network=self._network)

        s = io.BytesIO()
        tx.stream(s)
        tx_as_hex = b2h(s.getvalue())
        return tx_as_hex
