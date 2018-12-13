import unittest

from models.eth.input_wallet import InputWallet
from models.eth.eth_transaction_distribution import EthTransactionDistribution


class EthTransactionDistributionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distribution = EthTransactionDistribution()

    def test_first_input_more_than_first_output(self):
        ins = [
            self._create_input("input1", 7000),
            self._create_input("input2", 3000)
        ]
        outs = [
            self._create_output("output1", 30),
            self._create_output("output2", 70)
        ]
        txs = self.distribution.get_transaction_intents(ins, outs)
        print(*txs, sep="\n")
        self.assertEqual(3000, txs[0].amount)
        self.assertEqual(4000, txs[1].amount)
        self.assertEqual(3000, txs[2].amount)

    def test_first_input_less_than_first_output(self):
        ins = [
            self._create_input("input1", 1000),
            self._create_input("input2", 9000)
        ]
        outs = [
            self._create_output("output1", 30),
            self._create_output("output2", 70)
        ]
        txs = self.distribution.get_transaction_intents(ins, outs)
        print(*txs, sep="\n")
        self.assertEqual(1000, txs[0].amount)
        self.assertEqual(2000, txs[1].amount)
        self.assertEqual(7000, txs[2].amount)

    @staticmethod
    def _create_input(address: str, amount):
        return InputWallet(priv="priv", pub="pub", address=address, balance=amount)

    @staticmethod
    def _create_output(address: str, amount):
        return address, amount
