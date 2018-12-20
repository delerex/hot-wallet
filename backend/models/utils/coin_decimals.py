
class CoinDecimals:

    _DECIMALS = {
        "BTC": 10,
        "ETH": 18,
        "LTC": 10
    }

    @classmethod
    def get_decimals(cls, symbol: str) -> int:
        if symbol not in cls._DECIMALS:
            raise ValueError(f"Unsupported symbol [{symbol}]. Supported: {cls._DECIMALS.keys()}")
        return cls._DECIMALS[symbol]
