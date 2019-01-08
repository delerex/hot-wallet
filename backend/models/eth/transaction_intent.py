from models.eth.input_wallet import InputWallet


class TransactionIntent:
    def __init__(self, in_wallet: InputWallet, out_address: str, amount: int):
        self.in_wallet = in_wallet
        self.out_address = out_address
        self.amount = amount
        self.tx = None

    def __repr__(self):
        return str({"in": self.in_wallet, "out": self.out_address, "amount": self.amount})
