import json
import os
from decimal import Decimal
from typing import Optional

import requests

from models.eos.eospy.cleos import Cleos
from models.eos.eospy.exceptions import EOSKeyError
from models.eos.eospy.keys import EOSKey, check_wif
from models.eos.eospy.types import Transaction, EOSEncoder
from models.eos.eospy.utils import sig_digest
from models.errors import ApiUnexpectedError, OperationFailed
from models.network_type import NetworkType


class EosRps:
    JUNGLE_ENDPOINTS = [
        "http://jungle2.cryptolions.io:80",
        "https://jungle2.cryptolions.io:443",
        "https://jungle.eosio.cr:443",
        "https://api.jungle.alohaeos.com:443",
        "http://145.239.133.201:8888",
        "https://jungle.eosn.io:443",
        "http://18.223.252.15:8888",
        "http://49.236.137.37:8880",
        "http://jungle.eosmetal.io:18888",
        "http://jungle2-eos.blckchnd.com:8888",
        "http://88.99.193.44:8888",
        "http://bp4-d3.eos42.io:8888",
        "http://88.12.21.79:8888",
        "http://150.95.198.181:8888",
        "https://jungle.eosphere.io:443",
        "http://nivm.net:8888",
        "http://213.202.230.42:8888",
        "http://213.202.230.42:8888",
        "http://107.182.23.236:8888",
        "http://194.44.30.52:5888",
    ]

    MAIN_ENPOINTS = [
        "https://eos.greymass.com"
    ]

    def __init__(self, network):
        self._version = "v1"
        self._network = network
        self.cleos = Cleos(self.get_host())

    def get_host(self, n=0):
        if self._network == NetworkType.TESTNET:
            host = self.JUNGLE_ENDPOINTS[n]
        else:
            host = self.MAIN_ENPOINTS[n]
        return host

    def get_endpoint(self, n=0):
        host = self.get_host(n=n)
        return host + "/" + self._version + "/"

    def handle_error(self, response):
        try:
            response_data = response.json()
        except:
            text = response.text
            raise ApiUnexpectedError(f"Unexpected api error: {text}")
        message = response_data["error"]["details"][0]["message"]
        raise OperationFailed(f"Operation failed with error: {message}")

    def request(self, method: str, path: str,
                params: Optional[dict] = None,
                data=None,
                json_data: Optional[dict] = None,
                error_handler=None) -> Optional[dict]:
        # TODO switch between endpoints if response is wrong
        if params is None:
            params = {}
        if error_handler is None:
            error_handler = self.handle_error
        url = self.get_endpoint() + path
        response = requests.request(method, url, params=params, json=json_data, data=data)
        if response.status_code in {200, 202}:
            result = response.json()
        else:
            if json_data is not None:
                payload = json.dumps(json_data)
            elif data is not None:
                payload = data
            else:
                payload = ""
            print("EOS request", method, url, payload,
                  "failed:", response.status_code, response.text)
            if error_handler is not None:
                error_handler(response)
            result = None
        return result

    def get_chain_info(self) -> Optional[dict]:
        return self.request("POST", "chain/get_info")

    def get_account(self, account_id) -> Optional[dict]:
        querystring = {"account_name": account_id}
        return self.request("POST", "chain/get_account", json_data=querystring)

    def get_balance(self, account_id) -> Optional[Decimal]:
        querystring = {"account": account_id, "currency": "EOS", "code": "eosio.token"}
        response = self.request("POST", "chain/get_currency_balance", json_data=querystring)
        if response is None:
            return response
        balance = None
        for item in response:
            (value, currency) = item.split(" ")
            if currency == "EOS":
                balance = Decimal(value)
        return balance

    def abi_json_to_bin(self, code, action, arguments):
        body = {'code': code, 'action': action, 'args': arguments}
        return self.request("POST", "chain/abi_json_to_bin", json_data=body)

    def get_block(self, block_num):
        return self.request("POST", "chain/get_block",
                            json_data={"block_num_or_id": block_num})

    def get_chain_lib_info(self):
        chain_info = self.request("POST", "chain/get_info")
        lib_info = self.get_block(chain_info['last_irreversible_block_num'])
        return chain_info, lib_info

    def push_transaction(self, transaction, keys, compression='none', timeout=30):
        ''' parameter keys can be a list of WIF strings or EOSKey objects or
         a filename to key file'''
        chain_info, lib_info = self.get_chain_lib_info()
        trx = Transaction(transaction, chain_info, lib_info)
        # encoded = trx.encode()
        digest = sig_digest(trx.encode(), chain_info['chain_id'])
        # sign the transaction
        signatures = []
        keys = [keys]

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
            'compression': compression,
            'transaction': trx.__dict__,
            'signatures': signatures
        }
        data = json.dumps(final_trx, cls=EOSEncoder)

        response = self.request("POST", 'chain/push_transaction', data=data)

        return response

    def send_transaction(self, sender, receiver, value, key):
        arguments = {
            "from": sender,  # sender
            "to": receiver,  # receiver
            "quantity": f"{value:.4f}" + " EOS",  # In EOS
            "memo": "",
        }
        print("EOS.send_transaction", arguments)
        payload = {
            "account": "eosio.token",
            "name": "transfer",
            "authorization": [{
                "actor": sender,
                "permission": "active",
            }],
        }
        # Converting payload to binary
        data = self.abi_json_to_bin(payload['account'], payload['name'], arguments)
        # Inserting payload binary form as "data" field in original payload
        payload['data'] = data['binargs']
        # final transaction formed
        trx = {"actions": [payload]}

        # use a string or EOSKey for push_transaction
        # use EOSKey:
        resp = self.push_transaction(trx, key)
        return resp