from models.eth.web3api.web3api import Web3Api


class Web3ApiService:

    def __init__(self, web3api: Web3Api):
        self._web3api = web3api

    async def get_balance(self, address: str, contract_address):
        contract = self._web3api.get_contract(contract_address)
        balance_raw = contract.get_balance(address)
        return balance_raw
