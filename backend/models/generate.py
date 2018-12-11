import base58
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from bitcoin import *
from mnemonic import Mnemonic


def generate_mnemonic() -> str:
    new_key = random_key()
    m = Mnemonic(language='english')
    mn = m.to_mnemonic(bytes(new_key[0:16].encode("ascii")))
    return mn


def generate_keys(mn):
    m = Mnemonic(language='english')
    seed = m.to_seed(mn, "")
    mk = bip32_master_key(seed)

    bitcoin_priv = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 0 + 2 ** 31), 2 ** 31)
    ethereum_priv = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 60 + 2 ** 31), 2 ** 31)

    print("Bitcoin PrivKey  : {}".format(bitcoin_priv))
    print("Ethereum PrivKey : {}".format(ethereum_priv))
    #    os.environ['CASHIER_PUB_BTC'] = bip32_privtopub( bitcoin_priv)
    #    os.environ['CASHIER_PUB_ETH'] = bip32_privtopub( ethereum_priv)
    return bitcoin_priv, ethereum_priv


def generate_encrypted_seed(mnemonic, password):
    m = Mnemonic(language='english')
    if password is None:
        return None

    password_hash = SHA256.new()
    password_hash.update(bytes(password.encode("ascii")))
    aes_key = password_hash.digest()

    seed = m.to_seed(mnemonic, "")

    seed_hash = SHA256.new()
    seed_hash.update(seed)
    seed_hash_b = seed_hash.digest()

    aes_cipher = AES.new(aes_key, AES.MODE_CBC, b"ComBoxPasswordIV")
    encrypted_seed = aes_cipher.encrypt(seed + seed_hash_b)

    base58_encrypted_seed = base58.b58encode(encrypted_seed)
    print("Encrypted root seed: {}".format(base58_encrypted_seed))
    btcxpub, ethxpub = seed_to_xpub_keys(seed)
    return base58_encrypted_seed.decode("ascii"), btcxpub, ethxpub


def decrypt_seed(seed, password=None):
    if seed is None:
        print("You must specifiy base58 encrypted seed")
        return None
    if password is None:
        return None
    bseed = base58.b58decode(seed)
    password_hash = SHA256.new()
    password_hash.update(password.encode("ascii"))
    aes_key = password_hash.digest()
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, b"ComBoxPasswordIV")
    decrypted_seed = aes_cipher.decrypt(bseed)

    seed_hash = SHA256.new()
    seed_hash.update(decrypted_seed[0:64])
    seed_hash_b = seed_hash.digest()

    if decrypted_seed[64:] != seed_hash_b:
        print("Incorrect seed checksum. Check password")
        return None

    return decrypted_seed[0:64]


def seed_to_xpub_keys(seed):
    mk = bip32_master_key(seed)

    bitcoin_priv = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 2 ** 31), 2 ** 31)
    ethereum_priv = bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 60 + 2 ** 31), 2 ** 31)

    bitcoin_pub = bip32_privtopub(bitcoin_priv)
    ethereum_pub = bip32_privtopub(ethereum_priv)

    return bitcoin_pub, ethereum_pub
