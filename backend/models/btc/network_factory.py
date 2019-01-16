from pycoin.networks.bitcoinish import Network
from pycoin.symbols import btc, xtn, ltc, xlt, bch, xch

from models.btc.symbols import xrp, xrp_testnet
from models.network_type import NetworkType
from models.utils.singleton import Singleton


class NetworkFactory(metaclass=Singleton):

    _NETWORKS = {
        "BTC": {
            NetworkType.MAIN: btc.network,
            NetworkType.TESTNET: xtn.network,
        },
        "LTC": {
            NetworkType.MAIN: ltc.network,
            NetworkType.TESTNET: xlt.network,
        },
        "BCH": {
            NetworkType.MAIN: bch.network,
            NetworkType.TESTNET: xch.network,
        },
        "XRP": {
            NetworkType.MAIN: xrp.network,
            NetworkType.TESTNET: xrp_testnet.network,
        },
    }

    def get_network(self, symbol: str, network_type: str) -> Network:
        if symbol not in self._NETWORKS:
            raise ValueError(f"Unsupported symbol {symbol}")
        if network_type not in self._NETWORKS[symbol]:
            raise ValueError(f"Unsupported network type: {network_type}, for symbol {symbol}")
        return self._NETWORKS[symbol][network_type]
