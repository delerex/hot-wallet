class Transaction:

    def __init__(self,
                 block_hash: str,
                 block_number: str,
                 addr_from: str,
                 addr_to: str,
                 gas: str,
                 gas_price: str,
                 tx_hash: str,
                 tx_input: str,
                 nonce: str,
                 r: str,
                 s: str,
                 transaction_index: str,
                 v: str,
                 value: str,
                 status: int = 1,
                 contract_address: str = None):
        self.block_hash = block_hash
        self.block_number = block_number
        self.addr_from = addr_from
        self.addr_to = addr_to
        self.gas = gas
        self.gas_price = gas_price
        self.tx_hash = tx_hash
        self.tx_input = tx_input
        self.nonce = nonce
        self.r = r
        self.s = s
        self.transaction_index = transaction_index
        self.v = v
        self.value = value
        self.status = status
        self.contract_address = contract_address

    def __str__(self):
        return f"Transaction(id={self.tx_hash}, from={self.addr_from}, to={self.addr_to}, value={self.value}, " \
               f"status={self.status})"

    def __repr__(self):
        return self.__str__()
