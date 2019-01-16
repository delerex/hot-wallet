import json
from typing import Dict

from models.asset.asset import Asset
from models.asset.asset_config import AssetConfig
from models.asset.asset_defaults import AssetDefaults
from models.network_type import NetworkType
from models.wallet_config import WalletConfig


def load_config() -> Dict[str, WalletConfig]:
    raw = _load_raw_config()
    return WalletConfig.from_dict(raw)


def _load_raw_config() -> dict:
    try:
        with open('config.json') as json_data:
            d = json.load(json_data)
            return d
    except:
        return {}


def save_config(config_json):
    cfg = _load_raw_config()
    for x in config_json:
        cfg[x] = config_json[x]

    with open('config.json', "w") as out_file:
        json.dump(cfg, out_file)


def load_network_type() -> str:
    try:
        with open('network_type.json') as json_data:
            d = json.load(json_data)
            return d["network_type"]
    except:
        return NetworkType.MAIN


def save_network_type(network_type: str):
    data = {
        "network_type": network_type
    }
    with open("network_type.json", "w") as out_file:
        json.dump(data, out_file)


def load_outs_file():
    try:
        with open('outs.json') as json_data:
            d = json.load(json_data)
            return d
    except:
        return {}


def save_outs_to_file(wallet, currency, outs, signature):
    outs_object = load_outs_file()
    if wallet not in outs_object:
        outs_object[wallet] = {}
    outs_object[wallet][currency] = {"outs": outs, "signature": signature}
    with open('outs.json', "w") as out_file:
        json.dump(outs_object, out_file)


def load_assets_file():
    try:
        with open('assets.json') as json_data:
            d = json.load(json_data)
            return AssetConfig.from_dict(d)
    except Exception:
        return AssetConfig.create_default()


def add_asset_to_file(asset: Asset):
    config = load_assets_file()
    config.add_asset(asset)
    data = config.to_dict()
    with open('assets.json', "w") as out_file:
        json.dump(data, out_file)
