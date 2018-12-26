import io

from mnemonic import Mnemonic
from pycoin.coins.Tx import Tx
from pycoin.coins.TxIn import TxIn
from pycoin.coins.TxOut import TxOut
from pycoin.coins.tx_utils import create_tx
from pycoin.networks.bitcoinish import Network
from pycoin.encoding.hexbytes import b2h
from pycoin.symbols import btc, xtn
from pycoin.coins.tx_utils import sign_tx
from pycoin.ui.key_from_text import key_from_text

from models.btc.chain_so_explorer import ChainSoExplorer
from models.network_type import NetworkType


def standard_tx(coins_from, coins_to, network):
    txs_in = []
    unspents = []
    for h, idx, tx_out in coins_from:
        txs_in.append(TxIn(h, idx))
        unspents.append(tx_out)

    txs_out = []
    for coin_value, bitcoin_address in coins_to:
        txs_out.append(TxOut(coin_value, network.ui.script_for_address(bitcoin_address)))

    version, lock_time = 1, 0
    tx = Tx(version, txs_in, txs_out, lock_time)
    tx.set_unspents(unspents)
    return tx


m = Mnemonic(language="English")
# words = m.generate()
words = "noble suffer siege usage attract network noodle perfect humor figure check upset"

seed = m.to_seed(words)
print(words)
print(seed)


print()

ltc_network: Network = btc.network
print(ltc_network)

BIP32Node = ltc_network.ui._bip32node_class
# master key from seed
master_key = BIP32Node.from_master_secret(seed)

print(master_key)

btc_testnet_network = xtn.network
BIP32Node = btc_testnet_network.ui._bip32node_class
master_key_testnet = BIP32Node.from_master_secret(seed)

print(master_key_testnet)

print(master_key.address())
print(master_key_testnet.address())

# get coin type for bip-44
# print(master_key.netcode())
# network = networks.network_for_netcode(master_key.netcode())
# print(network.__dict__)
# create account key
account_key = master_key_testnet.subkey_for_path("44p/0p/0p")
# get xpub of account wallet
print()
print("account wallet:")
print(account_key)
print(account_key.public_pair())
print(account_key.sec())
print(account_key.sec_as_hex())
print(account_key.sec_as_hex(use_uncompressed=False))
print()
print(account_key.as_text())
account_xpub = account_key.as_text()

# get xpriv of account wallet
print(account_key.as_text(as_private=True))
# get account address
print(account_key.address())
# create address wallet
address_wallet = account_key.subkey_for_path("0/0")
# get address of address wallet
print()
print("Address wallet:")
print(address_wallet)
print(address_wallet.address())
# create address wallet from account xpub
print()
print("Generate address wallet from account xpub:")
address_wallet_pub = key_from_text(account_xpub, networks=[btc_testnet_network])\
    .subkey_for_path("0/0")
print(address_wallet_pub.address())

# create tx for address wallet
address_wallet_address = address_wallet_pub.address()

chain_so = ChainSoExplorer.from_symbol_and_network_type("BTC", network_type=NetworkType.TESTNET)
# in_txs = chain_so.get_input_transactions(address_wallet_address)
in_tx = chain_so.spendables_for_address(address_wallet_address)
print()
print("Transaction:")
print(f"in_tx: {in_tx} , type: {type(in_tx)}")
tx = create_tx(in_tx, ["mwCpnJ1PNULsdhy6cFrGAarcoqjB1r4Va3"], network=btc_testnet_network)
print(tx)
print()
# sign tx for address wallet

sign_tx(tx, [address_wallet.wif(False), address_wallet.wif(True)], network=btc_testnet_network)
print("Signed tx:")
print()

# send signed tx to blockchain
s = io.BytesIO()
tx.stream(s)
tx_as_hex = b2h(s.getvalue())
chain_so.send_transaction(tx_as_hex)

