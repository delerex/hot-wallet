from tronapi import Tron
import logging

from tronapi.providers.base import BaseProvider
from tronapi.trx import Trx

app_log = logging.getLogger(__name__)


class TronApi:
    def __init__(self, full_node: BaseProvider, solidity_node: BaseProvider, event_server: str):
        self.tron = Tron(full_node=full_node,
                         solidity_node=solidity_node,
                         event_server=event_server)
        self.trx: Trx = self.tron.trx

    def get_balance(self, address) -> int:
        return self.trx.get_balance(address, False)

    def create_transaction(self, out_address: str, amount: float, in_address: str):
        return self.tron.transaction_builder \
            .send_transaction(out_address, amount, in_address)

    def send_transaction(self, signed_transaction):
        return self.trx.broadcast(signed_transaction)
