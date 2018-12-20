import abc
from typing import List

from models.btc.input_transaction import InputTransaction


class BtcService(abc.ABC):

    @abc.abstractmethod
    def get_balance(self, address) -> int:
        pass

    @abc.abstractmethod
    def get_input_transactions(self, address) -> List[InputTransaction]:
        pass

    @abc.abstractmethod
    def get_fee_rate(self) -> float:
        pass

    @abc.abstractmethod
    def send_transaction(self, tx_hash):
        pass
