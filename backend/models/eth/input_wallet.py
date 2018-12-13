class InputWallet:

    def __init__(self, priv, pub, address, balance):
        self.priv = priv
        self.pub = pub
        self.address = address
        self.balance = balance

    def __repr__(self):
        return str({"address": self.address, "balance": self.balance})