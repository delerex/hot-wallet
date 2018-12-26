from models.btc.btccom_explorer import BtcComExplorer
from models.network_type import NetworkType


explorer = BtcComExplorer(symbol="BCH", network_type=NetworkType.MAIN)
balance = explorer.get_balance("1JAWMkEmv6gTRN7wNeyrezarf32zDwNqj4")
print(f"balance: {balance}")
