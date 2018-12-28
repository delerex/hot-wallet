from typing import Dict, List

from models.asset.asset import Asset, AssetErc20
from models.asset.asset_defaults import AssetDefaults
from models.asset.asset_type import AssetType


class AssetConfig:

    def __init__(self, assets: Dict[str, Asset]):
        self.assets = assets

    def to_dict(self):
        items = []
        for asset in self.assets.values():
            data = {
                "symbol": asset.symbol,
                "decimals": asset.decimals,
                "coin_index": asset.coin_index,
                "type": asset.asset_type,
            }
            if isinstance(asset, AssetErc20):
                data["contract_address"] = asset.contract_address
            items.append(data)
        return items

    def add_asset(self, asset: Asset):
        if asset.symbol in self.assets:
            raise ValueError(f"{asset.symbol} already in assets")
        self.assets[asset.symbol] = asset

    @classmethod
    def from_dict(cls, data: list):
        result = {}
        for item in data:
            asset = cls._create_asset_from_dict(item)
            result[asset.symbol] = asset
        return AssetConfig(
            result
        )

    @staticmethod
    def _create_asset_from_dict(item):
        asset_type = item["type"]
        if asset_type == AssetType.BASE:
            asset = Asset(
                symbol=item["symbol"],
                decimals=item["decimals"],
                coin_index=item["coin_index"],
            )
        elif asset_type == AssetType.ERC20:
            asset = AssetErc20(
                symbol=item["symbol"],
                decimals=item["decimals"],
                coin_index=item["coin_index"],
                contract_address=item["contract_address"],
            )
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")
        return asset

    @classmethod
    def create_default(cls):
        data = {asset.symbol: asset for asset in AssetDefaults.LIST}
        return AssetConfig(data)
