class Wallet:

    def __init__(self, seed, xpub, data=None):
        self.seed = seed
        self.xpub = xpub
        self.data = data