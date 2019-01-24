import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from aiohttp import web
from aiohttp.web_request import BaseRequest, Request

from api.middleware import error_handling_middleware, cors_middleware, \
    request_and_auth_data_middleware
from models.accounting import API as AccounttingAPI
from models.asset.asset import AssetErc20, Asset
from models.asset.asset_defaults import AssetDefaults
from models.btc.btc_model import BitcoinClass
from models.eth.erc20_model import Erc20Model
from models.factory.currency_model_factory import CurrencyModelFactory
from models.generate import decrypt_seed
from models.generate import generate_mnemonic, generate_encrypted_seed
from models.network_type import NetworkType
from models.wallet_config import WalletConfig
from repositories.config_repository import load_config, save_config, save_outs_to_file, \
    load_outs_file, \
    load_network_type, save_network_type, load_assets_file, add_asset_to_file

PORT = 3200

accounting = AccounttingAPI(None)


async def check(request):
    return {"error": None, "result": "server"}


async def login(request: Request):
    res = accounting.login(request.all_data["user"], request.all_data["password"])
    if res is None:
        return {"error": "Problem with login", "result": None}
    return {"error": None, "result": res}


async def withdrawal_requests(request: Request):
    res = accounting.get_reported_transactions()
    return {"error": None, "result": res}


async def get_mnemonic(request: Request):
    res = generate_mnemonic()
    return {"error": None, "result": res}


async def add_wallet(request: Request):
    wallet_id = request.match_info.get('wallet', None)
    config = load_config()
    if wallet_id in config and not config[wallet_id].has_encrypted_seed():
        return {"error": "Seed phrase is already set"}
    network_type = request.all_data["network_type"]
    mnemonic = request.all_data["mnemonic"]
    key_password = request.all_data["keypassword"]
    encrypted_seed = generate_encrypted_seed(mnemonic,
                                             key_password)
    decrypted_seed = decrypt_seed(encrypted_seed, key_password)
    assets = load_assets_file()
    xpubs = {}
    for asset in assets.assets.values():
        xpubs[asset.symbol] = generate_xpub(asset, network_type, decrypted_seed)

    cfg = WalletConfig(
        wallet_id=wallet_id,
        wallet_type=request.all_data["wallettype"],
        network_type=network_type,
        encrypted_seed=str(encrypted_seed),
        xpubs=xpubs,
        data={},
    )
    save_config(cfg.to_dict())
    return {"error": None, "result": True}


def generate_xpub(asset: Asset, network_type, seed):
    factory = CurrencyModelFactory()
    model = factory.get_currency_model_for_asset(asset, network_type)
    xpub = model.generate_xpub(seed)
    return xpub


async def get_wallets(request: Request):
    config = load_config()
    wallets = []
    for w in config:
        if isinstance(config[w], WalletConfig):
            wallets.append(w)

    return {"error": None, "result": wallets}


async def get_wallet(request: Request):
    config = load_config()
    outs = load_outs_file()
    wallet_id = request.match_info.get('wallet', None)
    res = {}
    wallet = config[wallet_id]
    for symbol, xpub in wallet.xpubs.items():
        res[symbol] = {
            "pub": xpub,
            "outs": outs.get(wallet_id, {}).get(symbol, {}).get("outs", None),
        }
        if symbol in wallet.data:
            data = wallet.data[symbol]
            res[symbol]["data"] = data

    return {"error": None, "result": res}


async def get_balance(request: Request):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    number = request.match_info.get('number', None)

    config = load_config()
    if wallet_id not in config:
        return {"error": f"Not found wallet [{wallet_id}]"}
    wallet_config = config[wallet_id]

    network_type = load_network_type()
    factory = CurrencyModelFactory()

    assets = load_assets_file()
    asset = assets.assets[currency]

    currency_model = factory.get_currency_model_for_asset(asset, network_type)
    xpubkey = currency_model.get_xpub(wallet_config)
    if xpubkey is None:
        return {"error": "Cannot get address"}
    addr = _get_address(wallet_config, currency_model, xpubkey, number)
    if addr is not None and number.lower() == "fee":
        if isinstance(currency_model, Erc20Model):
            balance = currency_model.get_fee_wallet_balance(addr)
        else:
            balance = 0
    else:
        balance = currency_model.get_balance(addr)
    return {"error": None, "result": balance}


def _get_address(wallet_config: WalletConfig, currency_model, xpubkey, number):
    if number.lower() == "fee":
        if isinstance(currency_model, Erc20Model):
            addr = currency_model.get_fee_wallet_address(xpub=xpubkey)
        else:
            addr = None
    else:
        if currency_model.currency == "EOS":
            return wallet_config.data.get("EOS", {}).get("account_id")
        addr = currency_model.get_addr_from_pub(xpubkey, number)
    return addr


async def get_address(request: BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    number = request.match_info.get('number', None)
    config = load_config()
    if wallet_id not in config:
        return {"error": f"Not found wallet [{wallet_id}]"}
    wallet_config = config[wallet_id]
    network_type = load_network_type()
    factory = CurrencyModelFactory()
    assets = load_assets_file()
    asset = assets.assets[currency]
    currency_model = factory.get_currency_model_for_asset(asset, network_type)
    xpubkey = currency_model.get_xpub(wallet_config)
    if xpubkey is None:
        return {"error": "Cannot get address"}

    addr = _get_address(wallet_config, currency_model, xpubkey, number)

    return {"error": None, "result": addr}


async def set_outs(request: BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    password = request.all_data.get("password")
    outs = request.all_data.get("outs")
    config = load_config()
    network_type = load_network_type()
    masterwallet = config.get("Master", None)
    if masterwallet is None or not masterwallet.has_encrypted_seed():
        return {"error": "No master wallet", "result": None}
    masterseed = decrypt_seed(masterwallet.encrypted_seed, password)
    if masterseed is None:
        return {"error": "Problems with master wallet", "result": None}
    btc_model = BitcoinClass(network_type)
    _priv, _pub, _addr = btc_model.get_priv_pub_addr(masterseed, 0)
    signature = btc_model.sign_data(json.dumps(outs), _priv)
    verify_result = btc_model.verify_data(json.dumps(outs), signature, _pub)
    if verify_result:
        save_outs_to_file(wallet_id, currency, outs, signature)
    return {"error": None, "result": verify_result}


async def send_transactions(request: Request):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    password = request.all_data.get("password", None)
    start = request.all_data.get("start", None)
    end = request.all_data.get("end", None)

    if start is None:
        return {"error": "No start field", "result": None}
    if end is None:
        return {"error": "No end field", "result": None}

    config = load_config()

    masterwallet = config.get("Master", None)
    if masterwallet is None or not masterwallet.has_encrypted_seed():
        return {"error": "No master wallet", "result": None}

    wallet_config = config.get(wallet_id, None)
    if wallet_config is None or not wallet_config.has_encrypted_seed():
        return {"error": f"No wallet [{wallet_id}]", "result": None}
    walletseed = decrypt_seed(wallet_config.encrypted_seed, password)
    if walletseed is None:
        return {"error": f"Problems with [{wallet_id}] wallet", "result": None}

    network_type = load_network_type()
    outs = load_outs_file()
    if wallet_id not in outs:
        return {"error": f"No outs for wallet [{wallet_id}]", "result": None}
    wallet_outs = outs[wallet_id]
    if currency not in wallet_outs:
        return {"error": f"No outs for wallet [{wallet_id}] and currency [{currency}]",
                "result": None}
    currency_outs: dict = wallet_outs[currency]["outs"]

    wallet = wallet_config.get_wallet(currency, decrypted_seed=walletseed)

    factory = CurrencyModelFactory()

    assets = load_assets_file()
    asset = assets.assets[currency]
    currency_model = factory.get_currency_model_for_asset(asset, network_type)

    # TODO сheck signature
    # btc_model = BitcoinClass()
    # signature = currency_outs[currency]["signature"]
    # verify_result = btc_model.verify_data(json.dumps(outs), signature, masterwallet.btc_xpub)
    # if not verify_result:
    #     return {"error": f"Wrong outs signature", "result": None}
    # print(f"send_transaction, verify_result: {verify_result}")

    print(f"currency_outs: {currency_outs}")
    currency_outs: dict = wallet_outs[currency]["outs"]
    currency_model.send_transactions(wallet, currency_outs, start, end)

    return {"error": None, "result": True}


async def get_network_type(request: Request):
    network_type = load_network_type()
    return {"error": None, "result": {
        "network_type": network_type
    }}


async def put_network_type(request: Request):
    network_type = request.all_data["network_type"]
    if network_type not in NetworkType.ALL:
        return {"error": f"Unknown network_type: {network_type}", "result": None}
    save_network_type(network_type)
    return {"error": None, "result": True}


async def get_assets(request: Request):
    asset_config = load_assets_file()
    return {"error": None, "result": {
        "assets": asset_config.to_dict()
    }}


async def post_asset(request: Request):
    asset_data = request.all_data.get("asset", None)
    password = request.all_data.get("password", None)

    config = load_config()
    masterwallet = config.get("Master", None)
    if masterwallet is None or not masterwallet.has_encrypted_seed():
        return {"error": "No master wallet", "result": None}
    masterseed = decrypt_seed(masterwallet.encrypted_seed, password)
    if masterseed is None:
        return {"error": "Problems with master wallet", "result": None}

    if asset_data is None:
        return {"error": "No asset object", "result": None}
    asset_config = load_assets_file()
    symbol = asset_data["symbol"]
    if symbol in asset_config.assets:
        return {"error": f"Asset with symbol {symbol} already exists", "result": None}
    asset = AssetErc20(
        symbol=symbol,
        contract_address=asset_data["contract_address"],
        coin_index=int(asset_data["coin_index"]),
        decimals=int(asset_data["decimals"]),
    )

    network_type = load_network_type()
    for wallet in config.values():
        seed = decrypt_seed(wallet.encrypted_seed, password)
        wallet.xpubs[symbol] = generate_xpub(asset, network_type, seed)

    # save results only after all manipulations
    add_asset_to_file(asset)
    for wallet in config.values():
        save_config(wallet.to_dict())

    return {"error": None, "result": True}


async def post_eos_account(request: Request):
    password = request.all_data.get("password", None)
    account_id = request.all_data.get("account_id", None)

    if account_id is None:
        return {"error": "Parameter account_id is required", "result": None}

    config = load_config()
    masterwallet = config.get("Master", None)
    if masterwallet is None or not masterwallet.has_encrypted_seed():
        return {"error": "No master wallet", "result": None}
    masterseed = decrypt_seed(masterwallet.encrypted_seed, password)
    if masterseed is None:
        return {"error": "Problems with master wallet", "result": None}

    for wallet in config.values():
        eos_data = wallet.data.get("EOS", {})
        if "account_id" in eos_data:
            return {"error": "Account has already set", "result": None}
        eos_data["account_id"] = account_id
        wallet.data["EOS"] = eos_data
        save_config(wallet.to_dict())

    return {"error": None, "result": True}


routes = [
    ("*", r"/api/check/", check),
    ("*", r"/api/", check),
    ("GET", r"/api/mnemonic/", get_mnemonic),
    ("POST", r"/api/wallets/{wallet}/", add_wallet),
    ("GET", r"/api/wallets/", get_wallets),
    ("GET", r"/api/wallets/{wallet}/", get_wallet),
    ("GET", r"/api/wallets/{wallet}/{currency}/{number}/address/", get_address),
    ("GET", r"/api/wallets/{wallet}/{currency}/{number}/balance/", get_balance),
    ("POST", r"/api/wallets/{wallet}/{currency}/outs/", set_outs),
    ("POST", r"/api/wallets/{wallet}/{currency}/transactions/", send_transactions),
    ("POST", r"/api/login/", login),
    ("GET", r"/api/tokens/requests", withdrawal_requests),
    ("GET", r"/api/network/type/", get_network_type),
    ("PUT", r"/api/network/type/", put_network_type),
    ("GET", r"/api/assets/", get_assets),
    ("POST", r"/api/assets/", post_asset),
    ("POST", r"/api/chain/eos/account/", post_eos_account),
]


async def init(loop, host="0.0.0.0", port=PORT):
    app = web.Application(
        loop=loop,
        client_max_size=128 * 1024 * 1024,
        middlewares=[cors_middleware, error_handling_middleware, request_and_auth_data_middleware]
    )

    for route in routes:
        print(route)
        app.router.add_route(*route)

    app.router.add_static('/', path='../frontend/', name='static')

    loop.set_default_executor(ThreadPoolExecutor(max_workers=3))

    handler = app.make_handler(access_log_format="%s %r (%a) %Tfsec")
    server_generator = loop.create_server(handler, host, port)
    return server_generator, handler, app


async def shutdown(server, app, handler):
    server.close()
    await server.wait_closed()
    await app.shutdown()
    # await handler.finish_connections(10.0)
    await app.cleanup()


def main():
    remote_loop = asyncio.get_event_loop()
    server_generator, handler, app = remote_loop.run_until_complete(init(remote_loop, port=PORT))
    server = remote_loop.run_until_complete(server_generator)

    try:
        print("Starting IOLoop...")
        remote_loop.run_forever()
    except KeyboardInterrupt:
        print("Starting shutdown...")
    finally:
        remote_loop.run_until_complete(shutdown(server, app, handler))
        remote_loop.close()


if __name__ == "__main__":
    main()
