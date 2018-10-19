from concurrent.futures import ThreadPoolExecutor
import asyncio
from aiohttp import web
from api.middleware import error_handling_middleware, cors_middleware, request_and_auth_data_middleware
from models.accounting import API as AccounttingAPI
from repositories.config_repository import load_config, save_config, save_outs_to_file, load_outs_file
from models.generate import generate_mnemonic, generate_keys, generate_encrypted_seed
from models.btc_model import BitcoinClass
from models.eth_model import EthereumClass
from models.generate import decrypt_seed
import json

from aiohttp.web_request import BaseRequest
PORT = 3200

accounting = AccounttingAPI(None)

async def check(request):
    return {"error" : None, "result" : "server"}


async def login(request : BaseRequest):
    res = accounting.login(request.all_data["user"], request.all_data["password"])
    if res is None:
        return {"error" : "Problem with login", "result" : None}
    return {"error" : None, "result" : res}

async def withdrawal_requests(request : BaseRequest):
    res = accounting.get_reported_transactions()
    return {"error" : None, "result" : res}

async def get_mnemonic(request : BaseRequest):
    res = generate_mnemonic()
    return {"error": None, "result": res}

async def add_wallet(request : BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    config = load_config()
    if wallet_id in config and "encrypted_seed" in config["wallet_id"]:
        return {"error" : "Seed phrase is already set"}
    encrypted_seed, btc_pub, eth_pub = generate_encrypted_seed(request.all_data["mnemonic"], request.all_data["keypassword"])
    cfg = {wallet_id : {"type": "wallet", "encrypted_seed" : str(encrypted_seed), "BTC" : btc_pub, "ETH" : eth_pub }}
    save_config(cfg)
    return {"error" : None, "result" : True}

async def get_wallets(request : BaseRequest):
    config = load_config()
    wallets=[]
    for w in config:
        if config[w].get("type", None) == "wallet":
            wallets.append(w)

    return {"error" : None, "result" : wallets}

async def get_wallet(request : BaseRequest):
    config = load_config()
    outs = load_outs_file()
    wallet_id = request.match_info.get('wallet', None)
    res={
        "BTC": {"pub": config[wallet_id]["BTC"], "outs" : outs.get(wallet_id,{}).get("BTC",{}).get("outs", None)},
        "ETH": {"pub": config[wallet_id]["ETH"], "outs" : outs.get(wallet_id,{}).get("ETH",{}).get("outs", None)}
        }
    return {"error" : None, "result" : res}


async def get_balance(request : BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    number = request.match_info.get('number', None)
    config = load_config()
    if currency == "BTC":
        bitcoin = BitcoinClass()
        pubkey = config.get(wallet_id, {}).get("BTC", None)
        if pubkey is None:
            return {"error": "Cannot get address"}
        addr = bitcoin.get_addr_from_pub(pubkey, number)
        balance = bitcoin.get_balance(addr)
    if currency == "ETH":
        ethereum = EthereumClass()
        pubkey = config.get(wallet_id, {}).get("BTC", None)
        if pubkey is None:
            return {"error": "Cannot get address"}
        addr = ethereum.get_addr_from_pub(pubkey, number)
        balance = ethereum.get_balance(addr)
    return {"error" : None, "result" : balance }


async def get_address(request : BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    number = request.match_info.get('number', None)
    config = load_config()
    if currency == "BTC":
        pubkey = config.get(wallet_id, {}).get("BTC", None)
        if pubkey is None:
            return {"error": "Cannot get address"}
        addr = BitcoinClass().get_addr_from_pub(pubkey, number)
    if currency == "ETH":
        pubkey = config.get(wallet_id, {}).get("ETH", None)
        if pubkey is None:
            return {"error": "Cannot get address"}
        addr = EthereumClass().get_addr_from_pub(pubkey, number)

    return {"error" : None,  "result" : addr}

async def set_outs(request : BaseRequest):
    wallet_id = request.match_info.get('wallet', None)
    currency = request.match_info.get('currency', None)
    password = request.all_data.get("password")
    outs = request.all_data.get("outs")
    config = load_config()
    masterwallet = config.get("Master", None)
    if masterwallet is None or "encrypted_seed" not in masterwallet:
        return {"error": "No master wallet", "result": None}
    masterseed = decrypt_seed(masterwallet["encrypted_seed"], password)
    if masterseed is None:
        return {"error": "Problems with master wallet", "result": None}
    btc = BitcoinClass()
    _priv, _pub, _addr = btc.get_priv_pub_addr(masterseed, 0)
    signature = btc.sign_data(json.dumps(outs), _priv)
    verify_result = btc.verify_data(json.dumps(outs), signature, _pub)
    if verify_result:
        save_outs_to_file(wallet_id, currency, outs, signature)
    return {"error" : None,  "result" : verify_result}

routes = [
    ("*",       r"/check/", check),
    ("*",       r"/api/", check),
    ("GET",  r"/mnemonic/", get_mnemonic),
    ("POST", r"/wallets/{wallet}/", add_wallet),
    ("GET",  r"/wallets/", get_wallets),
    ("GET",  r"/wallets/{wallet}/", get_wallet),
    ("GET",  r"/wallets/{wallet}/{currency}/{number}/address/", get_address),
    ("GET" , r"/wallets/{wallet}/{currency}/{number}/balance/", get_balance),
    ("POST" , r"/wallets/{wallet}/{currency}/outs/", set_outs),
    ("POST", r"/login/", login),
    ("GET",  r"/tokens/requests", withdrawal_requests),
]


async def init(loop, host="0.0.0.0", port=PORT):
    app = web.Application(
        loop=loop,
        client_max_size=128 * 1024 * 1024,
        middlewares=[cors_middleware,error_handling_middleware, request_and_auth_data_middleware]
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

