import base58
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from bitcoin import *
from mnemonic import Mnemonic
import os
from models.network_type import NetworkType


def generate_mnemonic() -> str:
    new_key = bytearray(os.urandom(16))
    m = Mnemonic(language='english')
    mn = m.to_mnemonic(new_key)
    return mn


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

    aes_cipher = AES.new(aes_key, AES.MODE_CBC, b"Delerex2019IVIII")
    encrypted_seed = aes_cipher.encrypt(seed + seed_hash_b)

    base58_encrypted_seed = base58.b58encode(encrypted_seed)
    if not isinstance(base58_encrypted_seed, str):
        base58_encrypted_seed = base58_encrypted_seed.decode("ascii")
    return base58_encrypted_seed


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
    aes_cipher = AES.new(aes_key, AES.MODE_CBC,  b"Delerex2019IVIII")
    decrypted_seed = aes_cipher.decrypt(bseed)

    seed_hash = SHA256.new()
    seed_hash.update(decrypted_seed[0:64])
    seed_hash_b = seed_hash.digest()

    if decrypted_seed[64:] != seed_hash_b:
        print("Incorrect seed checksum. Check password")
        return None

    return decrypted_seed[0:64]
