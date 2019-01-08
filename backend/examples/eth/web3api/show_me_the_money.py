import rlp
from eth_utils import decode_hex

from ethereum import transactions
from web3 import Web3

from models.eth.eth_model import EthereumClass
from models.eth.web3api import contract_test_abi
from models.eth.web3api.contract_test import ContractTest
from models.eth.web3api.contract_test_abi import test_erc20abi
from models.eth.web3api.web3api_factory import Web3ApiFactory
from models.generate import generate_encrypted_seed, decrypt_seed
from models.network_type import NetworkType

encrypted_seed = generate_encrypted_seed("giraffe light bone hockey infant open luggage era "
                                         "glimpse praise success ginger", "qwer")
seed = decrypt_seed(encrypted_seed, "qwer")
eth_model = EthereumClass(network_type=NetworkType.TESTNET)
priv_key, pub_key, addr = eth_model.get_priv_pub_addr(seed, 0)
print("priv, pub, addr", priv_key, pub_key, addr)

contract_addr = "0x722dd3F80BAC40c951b51BdD28Dd19d435762180"

web3api_factory = Web3ApiFactory()
web3api = web3api_factory.create(NetworkType.TESTNET)
contract: ContractTest = web3api.get_contract(contract_addr,
                                              abi=test_erc20abi,
                                              clz=ContractTest)
transaction = contract.show_me_the_money(addr, 10 ** 18)
print(transaction)
tx_count = web3api.get_transaction_count(addr)
print("tx_count:", tx_count)
transaction["nonce"] = tx_count
tx = transactions.Transaction(nonce=tx_count,
                              to=contract_addr,
                              value=transaction["value"],
                              gasprice=transaction["gasPrice"],
                              startgas=transaction["gas"],
                              data=decode_hex(transaction["data"]))

chain_id = 3    # Ropsten id
signed = tx.sign(priv_key, chain_id)
unencoded_tx = rlp.encode(signed)
signed_tx = "0x" + unencoded_tx.hex()
result = web3api.send_raw_transaction(signed_tx)
print(result)
# tx_hash = self.etherscan.send_transaction(signed_tx)