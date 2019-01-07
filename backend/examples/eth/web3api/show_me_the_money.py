from models.eth.web3api import contract_test_abi
from models.eth.web3api.contract_test import ContractTest
from models.eth.web3api.contract_test_abi import test_erc20abi
from models.eth.web3api.web3api_factory import Web3ApiFactory
from models.network_type import NetworkType

web3api_factory = Web3ApiFactory()
web3api = web3api_factory.create(NetworkType.TESTNET)
contract: ContractTest = web3api.get_contract("0x722dd3F80BAC40c951b51BdD28Dd19d435762180",
                                              abi=test_erc20abi,
                                              clz=ContractTest)
contract.show_me_the_money("0x3F7aBaD32E7D563e81C55E154aDcF77A88E4A98f", 10**18)
