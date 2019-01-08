from typing import List, Dict

import rlp
from eth_utils import decode_hex
from ethereum import transactions

from models.errors import ApiInsufficientFund, ApiUnexpectedError
from models.eth.eth_model import EthereumClass
from models.eth.fee_wallet import FeeWallet
from models.eth.input_wallet import InputWallet
from models.eth.transaction_intent import TransactionIntent
from models.eth.web3api.contract_erc20 import ContractErc20


class Erc20Model(EthereumClass):

    def __init__(self, network_type, currency="ETH", decimals=18, coin_index=60,
                 contract_address=None):
        super().__init__(network_type, currency, decimals, coin_index, contract_address)
        self.fee_nonce = 0

    def get_fee_wallet_address(self, seed=None, xpub=None):
        # fee wallet path is r/44'/s'/0'/2/0
        if seed is not None:
            _, _, addr = self.get_priv_pub_addr(seed, 0, change=2)
        elif xpub is not None:
            addr = self.get_addr_from_pub(xpub, 0, change=2)
        else:
            raise ValueError("seed or xpub should be set")
        return addr

    def get_fee_wallet(self, seed):
        # fee wallet path is r/44'/s'/0'/2/0
        priv, pub, addr = self.get_priv_pub_addr(seed, 0, change=2)
        return FeeWallet(address=addr, priv_key=priv)

    def send_transactions(self, seed, outs_percent, start, end) -> List[str]:
        if isinstance(outs_percent, dict):
            outs_percent = [(key, value) for (key, value) in outs_percent.items()]
        # 1. get input wallets
        input_wallets = self._get_input_wallets(seed, start, end)
        print(f"send_transactions, input_wallets:\n {input_wallets}")
        # 2. distribute money and create intents
        input_wallets = [w for w in input_wallets if w.balance > 0]
        tx_intents = self._transaction_distribution.get_transaction_intents(input_wallets,
                                                                            outs_percent)
        print(f"send_transactions:\n {tx_intents}")
        gas_price = self.etherscan.gas_price
        txs = []
        nonce_dict = self._get_nonce_dict(input_wallets)
        # 3. create contract transactions
        for intent in tx_intents:
            intent: TransactionIntent = intent
            in_wallet = intent.in_wallet
            contract: ContractErc20 = self._web3api.get_contract(self.contract_address)
            transaction = contract.transfer(intent.out_address, intent.amount)
            tx = transactions.Transaction(nonce=nonce_dict[in_wallet.address],
                                          to=self.contract_address,
                                          value=transaction["value"],
                                          gasprice=transaction["gasPrice"],
                                          startgas=transaction["gas"],
                                          data=decode_hex(transaction["data"]))
            txs.append(tx)
            intent.tx = tx
            nonce_dict[in_wallet.address] += 1

        # 4. estimate fees
        total_fee = sum([tx.gasprice * tx.startgas for tx in txs])
        fee_wallet = self.get_fee_wallet(seed)
        self.check_fee_wallet_has_enough_balance(total_fee, fee_wallet.address)

        # 5. prepare balances for fee on ETH wallets
        self.prepare_input_wallets(tx_intents, gas_price, fee_wallet)

        # 6. sign and send transactions
        tx_hashes = self._sign_and_send_transactions(tx_intents)

        return tx_hashes

    def _sign_and_send_transactions(self, tx_intents):
        tx_hashes = []
        for intent in tx_intents:
            intent: TransactionIntent = intent
            in_wallet = intent.in_wallet
            signed = intent.tx.sign(in_wallet.priv, self.etherscan.chain_id)
            unencoded_tx = rlp.encode(signed)
            signed_tx = "0x" + unencoded_tx.hex()
            print("send transaction to", intent.out_address, "with nonce", intent.tx.nonce)
            tx_hash = self.etherscan.send_transaction(signed_tx)
            tx_hashes.append(tx_hash)
        return tx_hashes

    def check_fee_wallet_has_enough_balance(self, amount, fee_wallet_address):
        # get eth balance from etherscan
        fee_wallet_balance = int(self.etherscan.balance(fee_wallet_address))
        if fee_wallet_balance < amount:
            raise ApiInsufficientFund(message=f"On fee wallet [{fee_wallet_address}] "
                                              f"insufficient fund: required {amount}, "
                                              f"found {fee_wallet_balance}")

    def prepare_input_wallets(self, tx_intents: List[TransactionIntent], gas_price,
                              fee_wallet: FeeWallet):
        input_wallets: Dict[InputWallet, int] = {}
        for intent in tx_intents:
            fee_amount = input_wallets.get(intent.in_wallet, 0)
            fee_amount += intent.tx.gasprice * intent.tx.startgas
            input_wallets[intent.in_wallet] = fee_amount

        for in_wallet, fee_amount in input_wallets.items():
            self.prepare_input_wallet(in_wallet, fee_amount, gas_price, fee_wallet)

    def prepare_input_wallet(self, input_wallet: InputWallet, amount, gas_price,
                             fee_wallet: FeeWallet):
        estimated_gas = 21000
        nonce = self._web3api.get_transaction_count(fee_wallet.address)
        nonce = max(nonce, self.fee_nonce)
        tx = transactions.Transaction(nonce=nonce,
                                      to=input_wallet.address,
                                      value=amount,
                                      gasprice=gas_price,
                                      startgas=estimated_gas,
                                      data=b"")
        signed = tx.sign(fee_wallet.priv_key, self.etherscan.chain_id)
        unencoded_tx = rlp.encode(signed)
        signed_tx = "0x" + unencoded_tx.hex()
        tx_hash = self.etherscan.send_transaction(signed_tx)
        if tx_hash is None:
            raise ApiUnexpectedError(message=f"Error while filling input wallets with fee")
        self.fee_nonce = nonce + 1
