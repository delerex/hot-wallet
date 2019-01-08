import logging

from eth_utils import to_checksum_address
from web3.contract import Contract

app_log = logging.getLogger(__name__)


class ContractErc20:
    def __init__(self, contract: Contract):
        self.contract = contract

    def get_name(self):
        return self.contract.functions.name().call()

    def get_decimals(self):
        return self.contract.functions.decimals().call()

    def get_symbol(self):
        return self.contract.functions.symbol().call()

    def get_balance(self, address: str):
        address = to_checksum_address(address)
        return self.contract.functions.balanceOf(address).call()

    def get_transactions(self):
        app_log.warning("You are using experimental method. It may work wrong!")
        event_filter = self.contract.eventFilter('Transfer',
                                                 {
                                                      "filter": {"from": "0x44a37eafa941a91b6fcc4a03ed097b8ab0b8523c"}
                                                  })
        print(f"event_filter: {event_filter}, type is {type(event_filter)}")

    def transfer(self, address, value):
        address = to_checksum_address(address)
        return self.contract.functions.transfer(address, value).buildTransaction()
