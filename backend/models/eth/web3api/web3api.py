import logging
from datetime import datetime
from typing import Optional

from web3 import Web3
from web3.providers import BaseProvider

from models.eth.web3api.block import Block
from models.eth.web3api.contract_erc20 import ContractErc20
from models.eth.web3api.contract_erc20_abi import erc20abi
from models.eth.web3api.transaction import Transaction

app_log = logging.getLogger(__name__)


class Web3Api:
    def __init__(self, provider: BaseProvider):
        print("Web3 initing...")
        self.web3 = Web3(provider)
        print("Web3 inited")

    def get_network_type(self) -> str:
        return self.web3.eth.net.getNetworkType()

    def get_contract(self, address, abi=erc20abi, clz=ContractErc20) -> ContractErc20:
        contract = self.web3.eth.contract(abi=abi, address=self.web3.toChecksumAddress(address))
        return clz(contract)

    def get_transaction_count(self, address: str) -> int:
        return self.web3.eth.getTransactionCount(address)

    def send_raw_transaction(self, raw_transaction):
        return self.web3.eth.sendRawTransaction(raw_transaction)

    def get_block(self, block_identifier) -> Optional[Block]:
        start_time = datetime.now()
        block = self.web3.eth.getBlock(block_identifier=block_identifier, full_transactions=True)
        # app_log.info(f"get_block: {block_identifier}, block: {block}")
        if not block:
            return None
        return self._block_from_json(block)

    def get_last_block_number(self) -> int:
        return self.web3.eth.blockNumber

    def _block_from_json(self, data: dict) -> Block:
        # print(f"block_from_json: {data}")
        transactions = [self._transaction_from_json(tx) for tx in data["transactions"]]
        return Block(
            transactions=transactions,
            number=data["number"],
            hash_number=data["hash"].hex(),
            timestamp=data["timestamp"]
        )

    def _transaction_from_json(self, data: dict) -> Transaction:
        # print(f"transaction_from_json: {data}")
        tx_input = data["input"]
        contract_address = None
        addr_to = data["to"]
        value = data["value"]
        # ERC-20 token parsing
        if tx_input.startswith("0xa9059cbb") and len(tx_input) >= 11:
            try:
                end = 74
                contract_address = addr_to
                addr_to = tx_input[10:end]
                addr_to = hex(int(addr_to, 16))
                value = int(tx_input[end:], 16)
            except Exception as e:
                app_log.warning(f"wrong transaction: {data}")
                raise e
        return Transaction(
            block_hash=data["blockHash"].hex(),
            block_number=data["blockNumber"],
            addr_from=data["from"],
            addr_to=addr_to,
            gas=data["gas"],
            gas_price=data["gasPrice"],
            tx_hash=data["hash"].hex(),
            tx_input=data["input"],
            nonce=data["nonce"],
            r=data["r"].hex(),
            s=data["s"].hex(),
            transaction_index=data["transactionIndex"],
            v=data["v"],
            value=value,
            contract_address=contract_address
        )

    def update_transaction_with_receipt(self, tx: Transaction) -> bool:
        receipt = self.get_transaction_receipt(tx)
        tx.status = receipt["status"]
        tx.gas = receipt["gasUsed"]
        return True

    def get_transaction_receipt(self, tx: Transaction) -> dict:
        data = self.web3.eth.getTransactionReceipt(tx.tx_hash)
        return data