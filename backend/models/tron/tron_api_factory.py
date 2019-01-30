import logging
from _ast import Dict

from tronapi import HttpProvider

from models.network_type import NetworkType
from models.tron.tron_api import TronApi
from models.utils.singleton import Singleton

app_log = logging.getLogger(__name__)


class TronApiFactory(metaclass=Singleton):

    def __init__(self):
        self.apis: Dict[str, TronApi] = {}

    def create(self, network_type: str):
        if network_type in self.apis:
            return self.apis[network_type]
        if network_type == NetworkType.MAIN:
            full_node = HttpProvider("https://api.trongrid.io")
            solidity_node = HttpProvider("https://api.trongrid.io")
            event_server = "https://api.trongrid.io"
            api = TronApi(full_node=full_node, solidity_node=solidity_node,
                          event_server=event_server)
        elif network_type == NetworkType.TESTNET:
            full_node = HttpProvider("https://api.shasta.trongrid.io")
            solidity_node = HttpProvider("https://api.shasta.trongrid.io")
            event_server = "https://api.shasta.trongrid.io"
            api = TronApi(full_node=full_node, solidity_node=solidity_node,
                          event_server=event_server)
        else:
            raise NotImplementedError(f"network_type {network_type} is not supported yet")
        self.apis[network_type] = api
        return api