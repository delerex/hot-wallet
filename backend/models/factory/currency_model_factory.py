from typing import Dict

from models.btc.btc_model import BitcoinClass
from models.currency_model import CurrencyModel
from models.eth.eth_model import EthereumClass
from models.explorers.btccom_explorer import BtcComExplorer
from models.explorers.chain_so_explorer import ChainSoExplorer
from models.utils.singleton import Singleton


class CurrencyModelFactory(metaclass=Singleton):

    def __init__(self):
        self._models: Dict[str, CurrencyModel] = {}

    def _get_key(self, currency, network_type):
        return currency + "-" + network_type

    def get_currency_model(self, currency: str, network_type: str) -> CurrencyModel:
        key = self._get_key(currency, network_type)
        if key in self._models:
            return self._models[key]
        if currency == "ETH":
            model = EthereumClass(network_type)
        elif currency == "BTC":
            model = BitcoinClass(network_type)
        elif currency == "BCH":
            model = BitcoinClass(network_type, symbol=currency,
                                 explorer=BtcComExplorer(currency, network_type))
        elif currency == "LTC":
            explorer = ChainSoExplorer.from_symbol_and_network_type(currency, network_type)
            model = BitcoinClass(network_type, symbol=currency, explorer=explorer)
        else:
            raise NotImplementedError(f"Unsupported currency: {currency}")
        self._models[key] = model
        return model
