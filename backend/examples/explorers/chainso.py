from pycoin.symbols import btc

from models.explorers.chain_so_explorer import ChainSoExplorer
from models.network_type import NetworkType

chain_so = ChainSoExplorer.from_symbol_and_network_type("BTC", network_type=NetworkType.MAIN)
# chain_so = ChainSoExplorer.from_symbol_and_network_type("BTC", network_type=NetworkType.TESTNET)
# in_txs = chain_so.get_input_transactions(address_wallet_address)
in_tx = chain_so.get_spendables_for_address("1KCS3Nvd56Hh2vEa6fhz9THw44BEnnyhjo")
# in_tx = chain_so.get_spendables_for_address("mwCpnJ1PNULsdhy6cFrGAarcoqjB1r4Va3")
print()
print("Transaction:")
print(f"in_tx: {in_tx} , type: {type(in_tx)}")
# txs = chain_so.get_transactions("mwCpnJ1PNULsdhy6cFrGAarcoqjB1r4Va3")
# print(json.dumps(txs))

network = btc.network
first = "1KCS3Nvd56Hh2vEa6fhz9THw44BEnnyhjo"        # b'v\xa9\x14J&\xe0b\xca\x95\xe2\x06\x0e\x9dl\xfc-V\x1dp\x19N\xa4\x1d\x88\xac'
second = "17A16QmavnUfCW11DAApiJxp7ARnxN5pGX"       # b'v\xa9\x14\xac\x14@\xecJn\xf5\x0f|\xcf\x14=\x18M\x1d\xe6\xf5\xf3\xf8\x92\x88\xac'
script1 = network.ui.script_for_address(first)
script2 = network.ui.script_for_address(second)
print(first, script1)
print(second, script2)
print(in_tx[0].script)

data = {"data": {"total_count": 1, "page": 1, "pagesize": 50, "list": [
    {"confirmations": 2, "block_height": 555562,
     "block_hash": "00000000000000000036796e586e6f5909ae07dd4918f3401cee98035155cc2a",
     "block_time": 1545823070, "created_at": 1545821853, "fee": 573,
     "hash": "e141a6b8afca35867089aab8e6f99ebb56d6adab9a4d81df965ec10433c8a602", "inputs_count": 1,
     "inputs_value": 40549751, "is_coinbase": False, "is_double_spend": False, "is_sw_tx": False,
     "weight": 900, "vsize": 225,
     "witness_hash": "e141a6b8afca35867089aab8e6f99ebb56d6adab9a4d81df965ec10433c8a602",
     "lock_time": 0, "outputs_count": 2, "outputs_value": 40549178, "size": 225, "sigops": 8,
     "version": 1, "inputs": [
        {"prev_addresses": ["15XfC5P9arPg6m21MNamVyK6A1BnQXLA9z"], "prev_position": 1,
         "prev_tx_hash": "a9ca2bf71a2510d57a7cb6efc9cca4eb24df84cb426a13f0604f00909f43e086",
         "prev_type": "P2PKH", "prev_value": 40549751, "sequence": 4294967295}], "outputs": [
        {"addresses": ["1MHuHYVUSLHUwrFgGCNzunXCA7VzmZDpwy"], "value": 3960030, "type": "P2PKH",
         "spent_by_tx": "dd80fab5ed4d88c3595df43ef86e86d3d284b320ead8b25851f8fa01b2fee997",
         "spent_by_tx_position": 0},
        {"addresses": ["1CcjarygokAAv5LUfvSmRzUtqEJgN8KHkz"], "value": 36589148, "type": "P2PKH",
         "spent_by_tx": None, "spent_by_tx_position": -1}], "balance_diff": 36589148}]},
        "err_no": 0, "err_msg": None}
