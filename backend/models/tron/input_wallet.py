class InputWallet:

    def __init__(self,
                 priv,
                 pub,
                 address,
                 balance,
                 available_bandwidth):
        self.priv = priv
        self.pub = pub
        self.address = address
        self.balance = balance
        self.available_bandwidth = available_bandwidth

    def __repr__(self):
        return str({"address": self.address,
                    "balance": self.balance,
                    "available_bandwidth": self.available_bandwidth})