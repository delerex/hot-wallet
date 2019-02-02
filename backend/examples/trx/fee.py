import json
from datetime import datetime
from time import sleep

from models.eth.input_wallet import InputWallet
from models.network_type import NetworkType
from models.tron.tron_model import TronModel

tron_model = TronModel(network_type=NetworkType.TESTNET)

priv = "ed61abb4b07aa2e5452afaf123e7c0ab981ff6285b4b7d21fc2b624d2f0580ad"
pub = "f9a10629683c059e1e30cbe6db90d136b7ebe6545941f704c6fb753570788cc0"
addr = "TBtrCi1hWc3PaPTCRSGKVL5uwDKCf8sEDW"
new_addr = "TUCFvd6Z66LAzEcEDFtvhc176Z4WwJK84D"

trx = tron_model.data_api.trx
new_account = trx.get_account(new_addr)
print("new_account", new_account)
account = trx.get_account(addr)

print(account)
print("current timestamp", datetime.now().timestamp())
print()

account_resource = trx.get_account_resource(addr)
print(json.dumps(account_resource, indent=2))

bandwidth = trx.get_band_width(addr)
print(json.dumps(bandwidth, indent=2))

tx = trx.get_transaction("354e43c9be6018413ea91712a1bc849279f48ac4cdcbc5bab5f6fc5bc542e255")
print()
# print("tx:", json.dumps(tx, indent=2))
tx_info = trx.get_transaction_info("354e43c9be6018413ea91712a1bc849279f48ac4cdcbc5bab5f6fc5bc542e255")
print("tx_info:", json.dumps(tx_info, indent=2))

# net_fee: 2680
# net_usage: 268

in_wallet = InputWallet(
    priv=priv,
    pub=pub,
    address=addr,
    balance=account["balance"]
)

for i in range(1):
    pass
    response = tron_model._send_transaction(10.0, in_wallet, "TBSiHGEt6LBQSpSpkSFEpHWpsUdEVDDabz")
    # response = tron_model._send_transaction(10.0, in_wallet, new_addr)
    # receipt = trx.get_transaction_info(response["transaction"]["txID"])
    # sleep(1)
    # print("receipt", json.dumps(receipt, indent=2))
