from typing import Dict


class WalletConfig:

    def __init__(self,
                 wallet_id: str,
                 wallet_type: str,
                 network_type: str,
                 encrypted_seed: str,
                 btc_xpub: str,
                 eth_xpub: str):
        self.wallet_id = wallet_id
        self.wallet_type = wallet_type
        self.network_type = network_type
        self.encrypted_seed = encrypted_seed
        self.btc_xpub = btc_xpub
        self.eth_xpub = eth_xpub

    def has_encrypted_seed(self) -> bool:
        return self.encrypted_seed and len(self.encrypted_seed) > 0

    def to_dict(self):
        return {self.wallet_id: {
            "type": "wallet",
            "wallettype": self.wallet_type,
            "network_type": self.network_type,
            "encrypted_seed": self.encrypted_seed,
            "BTC": self.btc_xpub,
            "ETH": self.eth_xpub}
        }

    @staticmethod
    def from_dict(data: dict) -> dict:
        result = {}
        for (key, value) in data.items():
            result[key] = WalletConfig(
                wallet_id=key,
                wallet_type=value["wallettype"],
                network_type=value["network_type"],
                encrypted_seed=value["encrypted_seed"],
                btc_xpub=value["BTC"],
                eth_xpub=value["ETH"]
            )
        return result
