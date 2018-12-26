from pycoin.symbols import xtn

from models.explorers.btccom_explorer import BtcComExplorer
from models.explorers.chain_so_explorer import ChainSoExplorer
from models.network_type import NetworkType
# b'v\xa9\x14J&\xe0b\xca\x95\xe2\x06\x0e\x9dl\xfc-V\x1dp\x19N\xa4\x1d\x88\xac'

network = xtn.network
first = "mnH2sSGrVDHUR6E8xsKAxn5r4DHPqn7DtS"        # b'v\xa9\x14J&\xe0b\xca\x95\xe2\x06\x0e\x9dl\xfc-V\x1dp\x19N\xa4\x1d\x88\xac'
second = "mwCpnJ1PNULsdhy6cFrGAarcoqjB1r4Va3"       # b'v\xa9\x14\xac\x14@\xecJn\xf5\x0f|\xcf\x14=\x18M\x1d\xe6\xf5\xf3\xf8\x92\x88\xac'
script1 = network.ui.script_for_address(first)
script2 = network.ui.script_for_address(second)
print(first, script1)
print(second, script2)

address = "1QCXvQgkfpKA9JmQfATfoQPQnfKyWKSHpG"
explorer = BtcComExplorer(symbol="BTC", network_type=NetworkType.MAIN)
balance = explorer.get_balance(address)
print(f"balance: {balance}")
# spendables_for_address()
spendables = explorer.get_spendables_for_address(address)
print(f"spendables: {spendables}")
chain_so = ChainSoExplorer.from_symbol_and_network_type("BTC", NetworkType.MAIN)
spendables2 = chain_so.get_spendables_for_address(address)
print(f"spendables: {spendables2}")

fee_rate = explorer.get_fee_rate()
print(f"fee_rate: {fee_rate}")
fee_rate2 = chain_so.get_fee_rate()
print(f"fee_rate: {fee_rate2}")
