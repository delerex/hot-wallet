from builtins import TypeError
from symbol import parameters
from typing import List

from hexbytes import HexBytes

from models.eth.web3api.transaction import Transaction


class Block:

    def __init__(self,
                 transactions: List[Transaction],
                 number: str,
                 hash_number: str,
                 timestamp: str):
        self.transactions: List[Transaction] = transactions
        self.number = number
        self.hash_number = hash_number
        self.timestamp = timestamp
        for (key, value) in self.__dict__.items():
            if isinstance(value, HexBytes):
                raise TypeError(f"{key} has invalid type: {type(value)}")

    def __str__(self):
        return f"Block(number={self.number}, timestamp={self.timestamp})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        data = self.__dict__.copy()
        data["transactions"] = [tx.__dict__ for tx in self.transactions]
        return data
