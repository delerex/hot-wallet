from eth_utils import to_checksum_address

from models.eth.web3api.contract_erc20 import ContractErc20


class ContractTest(ContractErc20):

    def __init__(self, contract):
        super().__init__(contract)

    def show_me_the_money(self, address, value):
        address = to_checksum_address(address)
        return self.contract.functions.showMeTheMoney(address, value).buildTransaction()
