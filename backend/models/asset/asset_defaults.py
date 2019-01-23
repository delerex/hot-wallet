from models.asset.asset import Asset


class AssetDefaults:

    LIST = [
        Asset("BTC", 8),
        Asset("LTC", 8),
        Asset("BCH", 8),
        Asset("ETH", 18),
        Asset("XRP", 6),
        Asset("EOS", 4),
    ]
