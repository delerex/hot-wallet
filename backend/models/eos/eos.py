import base58


class Eos:

    @staticmethod
    def seed_to_wif(seed) -> bytes:
        return base58.b58encode_check(bytes.fromhex("80") + seed)
