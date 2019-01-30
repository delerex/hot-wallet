import hashlib
import json
from typing import Dict

from models.currency_model import CurrencyModel
from models.eos.eos import Eos
from models.eos.eos_rpc import EosRpc
from models.eos.eospy.exceptions import EOSKeyError
from models.eos.eospy.keys import EOSKey, check_wif
from models.eos.eospy.types import Transaction, EOSEncoder
from models.eos.eospy.utils import sig_digest
from models.errors import ApiInsufficientFund, ApiObjectNotFound
from models.wallet import Wallet
from models.wallet_config import WalletConfig


class EosModel(CurrencyModel):

    def __init__(self, network_type):
        super().__init__("EOS")
        self.data_api = EosRpc(network_type)

    def generate_xpub(self, root_seed) -> str:
        wif = Eos.seed_to_wif(root_seed[:32])
        privkey = EOSKey(wif.decode())
        return privkey.to_public()

    def get_priv_pub_addr(self, root_seed, n) -> (str, str, str):
        priv_wif = Eos.seed_to_wif(root_seed[:32])
        privkey = EOSKey(priv_wif.decode())
        pubkey = privkey.to_public()
        return priv_wif, pubkey, pubkey

    def get_addr_from_pub(self, pubkey, address_number):
        return pubkey

    def get_xpub(self, wallet: WalletConfig) -> str:
        return wallet.xpubs.get("EOS")

    @property
    def decimals(self):
        return 4

    @staticmethod
    def generate_tag(seed, n) -> int:
        s = seed + str(n)
        return int(hashlib.sha1(s.encode()).hexdigest(), 16) % (2 ** 32)

    def get_balance(self, addr):
        balance = self._get_balance_raw(addr)
        return str(balance)

    def _get_balance_raw(self, addr):
        return self.data_api.get_balance(addr)

    def _create_transactions(self, source: str, outs_percent: Dict[str, int]):
        transactions = []
        balance = self._get_balance_raw(source)
        if balance == 0:
            raise ApiInsufficientFund()
        print("eos._create_transactions, balance", balance)
        for out_address, percent in outs_percent.items():
            amount = int(balance * percent / 100)
            if amount > 0:
                transactions.append(dict(
                    address=out_address,
                    amount=amount,
                ))
        return transactions

    def send_transactions(self, wallet: Wallet, outs_percent: Dict[str, int], start, end):
        if "account_id" not in wallet.data:
            raise ApiObjectNotFound("Set account_id before send transaction")
        account = wallet.data["account_id"]
        priv_key, pub_key, addr = self.get_priv_pub_addr(wallet.seed, 0)
        txs = self._create_transactions(account, outs_percent)
        result = []
        for tx in txs:
            payload = {
                "account": "eosio.token",
                "name": "transfer",
                "authorization": [{
                    "actor": account,
                    "permission": "active",
                }],
            }
            receiver = tx["address"]
            amount = tx["amount"]
            binargs = self.data_api.tx_abi_json_to_bin(account, receiver, amount)
            # Inserting payload binary form as "data" field in original payload
            payload['data'] = binargs
            # final transaction formed
            trx = {"actions": [payload]}

            # use a string or EOSKey for push_transaction
            # use EOSKey:

            chain_info, lib_info = self.data_api.get_chain_lib_info()
            trx = Transaction(trx, chain_info, lib_info)
            # encoded = trx.encode()
            digest = sig_digest(trx.encode(), chain_info['chain_id'])
            # sign the transaction
            signatures = []
            keys = [priv_key]

            for key in keys:
                if check_wif(key):
                    k = EOSKey(key)
                elif isinstance(key, EOSKey):
                    k = key
                else:
                    raise EOSKeyError('Must pass a WIF string or EOSKey')
                signatures.append(k.sign(digest))
            # build final trx
            final_trx = {
                "compression": "none",
                "transaction": trx.__dict__,
                "signatures": signatures
            }
            data = json.dumps(final_trx, cls=EOSEncoder)

            response = self.data_api.push_transaction(data)
            print("send_transaction response", response)
            result.append(response)
        return result

    def get_nonce(self, addr):
        pass
