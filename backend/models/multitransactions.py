class MultiTransactionClass:
    def __init__(self, currency=None, reference_id=None, desc=""):
        self.transaction = {"ins": [],
                            "outs": [],
                            "exts": [],
                            "inusers": [],
                            "outusers": [],
                            "inamount": 0,
                            "outamount": 0,
                            "extamount": 0,
                            "time": 0,
                            "desc": "",
                            "currency": currency,
                            "reference": reference_id,
                            "_id": reference_id,
                            "description": desc}

    def add_in(self, wallet_id, amount):
        role = None
        id = None
        self.transaction["inamount"] += amount
        self.ins.append({"wallet": wallet_id, "amount": amount, "user": None, "role": None})

    def add_out(self, wallet_id, amount):
        role = None
        id = None
        self.transaction["outamount"] += amount
        self.outs.append({"wallet": wallet_id, "amount": amount, "user": None, "role": None})

    def add_ext(self, wallet_id, amount):
        self.transaction["extamount"] += amount
        self.exts.append({"wallet": wallet_id, "amount": amount, "user": None, "role": None})

    @property
    def time(self):
        return int(self.transaction["time"])

    def settime(self, value):
        self.transaction["time"] = int(value)

    @property
    def ins(self):
        return self.transaction["ins"]

    @property
    def exts(self):
        return self.transaction["exts"]

    @property
    def commission(self):
        return self.transaction["commission"]

    def setcommission(self, value):
        self.transaction["commission"] = float(value)

    @property
    def outs(self):
        return self.transaction["outs"]

    @property
    def inusers(self):
        return self.transaction["inusers"]

    @property
    def outusers(self):
        return self.transaction["outusers"]

    @property
    def inamount(self):
        return self.transaction["inamount"]

    @property
    def outamount(self):
        return self.transaction["outamount"]

    @property
    def currency(self):
        return self.transaction["currency"]

    @property
    def reference(self):
        return self.transaction["reference"]

    def to_json(self):
        return self.transaction

    @staticmethod
    def from_json(transaction):
        t = MultiTransactionClass()
        t.transaction = transaction
        return t
