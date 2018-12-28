from models.asset.asset_type import AssetType
from models.asset.coin_types import CoinTypes


class Asset:

    def __init__(self,
                 symbol: str,
                 decimals: int,
                 coin_index: int = None,
                 asset_type: str = AssetType.BASE):
        """
        :param symbol: - symbol of asset
        :param decimals: - int, decimals of asset
        :param coin_index: - coin index from SLIP-44
        :param asset_type: - AssetType: BASE or ERC20
        """
        if coin_index is None:
            coin_index = CoinTypes.get_index(symbol)
        self.symbol = symbol
        self.coin_index = coin_index
        self.asset_type = asset_type
        self.decimals = decimals


class AssetErc20(Asset):

    def __init__(self,
                 symbol,
                 decimals: int,
                 coin_index: int,
                 contract_address: str):
        """
        :param symbol: - symbol of asset
        :param decimals: - int, decimals of asset
        :param coin_index: - coin index from SLIP-44
        :param contract_address: - hex address of contract of ERC20 token
        """
        super().__init__(symbol=symbol,
                         decimals=decimals,
                         coin_index=coin_index,
                         asset_type=AssetType.ERC20)
        self.contract_address = contract_address
