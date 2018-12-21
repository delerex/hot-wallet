import base58
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from bitcoin import *
from mnemonic import Mnemonic

from models.network_type import NetworkType


def generate_mnemonic() -> str:
    new_key = random_key()
    m = Mnemonic(language='english')
    mn = m.to_mnemonic(bytes(new_key[0:16].encode("ascii")))
    return mn


def generate_encrypted_seed(mnemonic, password):
    print(f"generate_encrypted_seed: {mnemonic}, {password}")
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

    print(f"encrypted_seed type: {type(encrypted_seed)}")
    base58_encrypted_seed = base58.b58encode(encrypted_seed)
    print(f"Encrypted root seed: {base58_encrypted_seed}, type: {type(base58_encrypted_seed)}")
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
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, b"ComBoxPasswordIV")
    decrypted_seed = aes_cipher.decrypt(bseed)

    seed_hash = SHA256.new()
    seed_hash.update(decrypted_seed[0:64])
    seed_hash_b = seed_hash.digest()

    if decrypted_seed[64:] != seed_hash_b:
        print("Incorrect seed checksum. Check password")
        return None

    return decrypted_seed[0:64]
