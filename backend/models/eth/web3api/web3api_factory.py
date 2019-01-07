import logging
from _ast import Dict

from web3 import HTTPProvider


from models.eth.web3api.web3api import Web3Api
from models.network_type import NetworkType
from models.utils.singleton import Singleton

app_log = logging.getLogger(__name__)


class Web3ApiFactory(metaclass=Singleton):

    def __init__(self):
        self.apis: Dict[str, Web3Api] = {}

    def create(self, network_type: str):
        if network_type in self.apis:
            return self.apis[network_type]
        if network_type == NetworkType.MAIN:
            api = Web3Api(HTTPProvider('https://mainnet.infura.io'))
        elif network_type == NetworkType.TESTNET:
            api = Web3Api(HTTPProvider('https://ropsten.infura.io'))
        else:
            raise NotImplementedError(f"network_type {network_type} is not supported yet")
        self.apis[network_type] = api
        return api
