
class CoinDecimals:

    _DECIMALS = {
        "BTC": 8,
        "ETH": 18,
        "LTC": 8,
        "BCH": 8,
    }

    @classmethod
    def get_decimals(cls, symbol: str) -> int:
        if symbol not in cls._DECIMALS:
            raise ValueError(f"Unsupported symbol [{symbol}]. Supported: {cls._DECIMALS.keys()}")
        return cls._DECIMALS[symbol]
