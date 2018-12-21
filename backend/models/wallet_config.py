from typing import Dict


class WalletConfig:

    def __init__(self,
                 wallet_id: str,
                 wallet_type: str,
                 network_type: str,
                 encrypted_seed: str,
                 xpubs: Dict[str, str]):
        self.wallet_id = wallet_id
        self.wallet_type = wallet_type
        self.network_type = network_type
        self.encrypted_seed = encrypted_seed
        self.xpubs = xpubs

    def has_encrypted_seed(self) -> bool:
        return self.encrypted_seed and len(self.encrypted_seed) > 0

    def to_dict(self):
        return {self.wallet_id: {
            "type": "wallet",
            "wallettype": self.wallet_type,
            "network_type": self.network_type,
            "encrypted_seed": self.encrypted_seed,
            "xpubs": self.xpubs}
        }

    @staticmethod
    def from_dict(data: dict) -> dict:
        result = {}
        for (key, value) in data.items():
            # migrate from old version (21.12.2018)
            xpubs = value.get("xpubs", {})
            if "BTC" in value:
                xpubs["BTC"] = value["BTC"]
            if "ETH" in value:
                xpubs["ETH"] = value["ETH"]
            # load other date
            result[key] = WalletConfig(
                wallet_id=key,
                wallet_type=value["wallettype"],
                network_type=value["network_type"],
                encrypted_seed=value["encrypted_seed"],
                xpubs=xpubs,
            )
        return result
