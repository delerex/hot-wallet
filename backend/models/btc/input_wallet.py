from typing import List

from models.btc.input_transaction import InputTransaction


class InputWallet:

    def __init__(self, priv, pub, address, balance, in_transactions: List[InputTransaction]):
        self.priv = priv
        self.pub = pub
        self.address = address
        self.balance = balance
        self.in_transactions = in_transactions

    def __repr__(self):
        return str({"address": self.address, "balance": self.balance})