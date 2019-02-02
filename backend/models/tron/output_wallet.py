
class OutputWallet:
    def __init__(self,
                 address: str,
                 is_exist: bool,
                 percentage: int,
                 amount: int = None):
        self.address = address
        self.is_exist = is_exist
        self.percentage = percentage
        self.amount = amount

    def __repr__(self):
        return f"{{{self.address}, {self.amount}}}"
