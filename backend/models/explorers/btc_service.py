import abc
from typing import List

from pycoin.coins.bitcoin.Spendable import Spendable

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

    @abc.abstractmethod
    def get_spendables_for_address(self, address) -> List[Spendable]:
        """
        Return a list of Spendable objects for the
        given bitcoin address. It needs to create transaction via pycoin library.
        """
