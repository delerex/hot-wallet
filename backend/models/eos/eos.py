import base58

from .crypto import PrivateKey, PublicKey


class Eos:

    @staticmethod
    def seed_to_wif(seed) -> bytes:
        return base58.b58encode_check(bytes.fromhex("80") + seed)

    @staticmethod
    def priv_from_wif(wif) -> PrivateKey:
        return PrivateKey.from_b58check(wif)

    @staticmethod
    def priv_to_pub(privkey: PrivateKey) -> PublicKey:
        return privkey.public_key

    @staticmethod
    def pub_to_string(pubkey: PublicKey) -> bytes:
        return pubkey.address()
