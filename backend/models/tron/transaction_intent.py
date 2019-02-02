from models.tron.input_wallet import InputWallet
from models.tron.output_wallet import OutputWallet


class TransactionIntent:
    def __init__(self,
                 in_wallet: InputWallet,
                 out_wallet: OutputWallet,
                 amount: int,
                 fee: int = 0):
        self.in_wallet: InputWallet = in_wallet
        self.out_wallet = out_wallet
        self.amount = amount
        self.tx = None
        self.fee = fee

    def __repr__(self):
        return str({"in": self.in_wallet,
                    "out": self.out_wallet,
                    "amount": self.amount,
                    "fee": self.fee})
