import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from aiohttp import web
from aiohttp.web_request import BaseRequest, Request

from api.middleware import error_handling_middleware, cors_middleware, request_and_auth_data_middleware
from models.accounting import API as AccounttingAPI
from models.btc_model import BitcoinClass
from models.factory.currency_model_factory import CurrencyModelFactory
from models.generate import decrypt_seed
from models.generate import generate_mnemonic, generate_encrypted_seed
from models.network_type import NetworkType
from models.wallet_config import WalletConfig
from repositories.config_repository import load_config, save_config, save_outs_to_file, load_outs_file, \
    load_network_type, save_network_type

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
    encrypted_seed, btc_xpub, eth_xpub = generate_encrypted_seed(request.all_data["mnemonic"],
                                                                 request.all_data["keypassword"])
    cfg = WalletConfig(
        wallet_id=wallet_id,
        wallet_type=request.all_data["wallettype"],
        network_type=network_type,
        encrypted_seed=str(encrypted_seed),
        btc_xpub=btc_xpub,
        eth_xpub=eth_xpub
    )
    save_config(cfg.to_dict())
    return {"error": None, "result": True}


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
    res = {
        "BTC": {"pub": config[wallet_id].btc_xpub, "outs": outs.get(wallet_id, {}).get("BTC", {}).get("outs", None)},
        "ETH": {"pub": config[wallet_id].eth_xpub, "outs": outs.get(wallet_id, {}).get("ETH", {}).get("outs", None)}
    }
    return {"error": None, "result": res}


async def get_balance(request: Request):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    number = request.match_info.get('number', None)
    config = load_config()
    if wallet_id not in config:
        return {"error": f"Not found wallet [{wallet_id}]"}
    network_type = load_network_type()
    wallet_config = config[wallet_id]
    factory = CurrencyModelFactory()
    currency_model = factory.get_currency_model(currency, network_type)
    xpubkey = currency_model.get_xpub(wallet_config)
    if xpubkey is None:
        return {"error": "Cannot get address"}
    addr = currency_model.get_addr_from_pub(xpubkey, number)
    balance = currency_model.get_balance(addr)
    return {"error": None, "result": balance}


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
    currency_model = factory.get_currency_model(currency, network_type)
    xpubkey = currency_model.get_xpub(wallet_config)
    if xpubkey is None:
        return {"error": "Cannot get address"}
    addr = currency_model.get_addr_from_pub(xpubkey, number)

    return {"error": None, "result": addr}


async def set_outs(request: BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    password = request.all_data.get("password")
    outs = request.all_data.get("outs")
    config = load_config()
    masterwallet = config.get("Master", None)
    if masterwallet is None or not masterwallet.has_encrypted_seed():
        return {"error": "No master wallet", "result": None}
    masterseed = decrypt_seed(masterwallet.encrypted_seed, password)
    if masterseed is None:
        return {"error": "Problems with master wallet", "result": None}
    btc = BitcoinClass()
    _priv, _pub, _addr = btc.get_priv_pub_addr(masterseed, 0)
    signature = btc.sign_data(json.dumps(outs), _priv)
    verify_result = btc.verify_data(json.dumps(outs), signature, _pub)
    if verify_result:
        save_outs_to_file(wallet_id, currency, outs, signature)
    return {"error": None, "result": verify_result}


async def send_transactions(request: Request):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    ns = request.all_data.get("ns", None)
    config = load_config()

    outs = load_outs_file()
    wouts = outs.get(wallet_id, {}).get(currency, {}).get("outs", None)

    # masterwallet = config.get("Master", None)
    # if masterwallet is None or "encrypted_seed" not in masterwallet:
    #     return {"error": "No master wallet", "result": None}
    # masterseed = decrypt_seed(masterwallet["encrypted_seed"], password)
    # if masterseed is None:
    #     return {"error": "Problems with master wallet", "result": None}
    # btc = BitcoinClass()
    # _priv, _pub, _addr = btc.get_priv_pub_addr(masterseed, 0)
    # signature = btc.sign_data(json.dumps(outs), _priv)
    # verify_result = btc.verify_data(json.dumps(outs), signature, _pub)
    # if verify_result:
    #     save_outs_to_file(wallet_id, currency, outs, signature)
    return {"error": None, "result": wouts}


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
    ("GET",  r"/api/network/type/", get_network_type),
    ("PUT",  r"/api/network/type/", put_network_type),
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
    app.db.close()
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
