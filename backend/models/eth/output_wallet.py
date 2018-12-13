class OutputWallet:

    def __init__(self, addr, amount):
        self.addr = addr
        self.amount = amount

    def __repr__(self):
        return str({"addr": self.addr, "amount": self.amount})