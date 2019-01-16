from models.network_type import NetworkType
from models.xrp.ripple_data_api import RippleDataApi
from models.xrp.ripple_jsonrpc import RippleJsonRpc

api = RippleJsonRpc(NetworkType.MAIN)
address = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
print(api.get_balance(address))

api = RippleJsonRpc(NetworkType.TESTNET)
address = "rJ75gSkqXhCubbpn4PguThBXitQKMhBdpr"
print(api.get_balance(address))
