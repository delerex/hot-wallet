import hashlib
import hmac

import mnemonic
from pbkdf2 import PBKDF2
from pycoin.encoding.hexbytes import h2b, b2h

from models.xrp.b58 import b2a_hashed_base58
from models.xrp.serialize import fmt_hex, to_bytes
from models.xrp.sign import get_ripple_from_secret, get_ripple_from_pubkey, root_key_from_seed, \
    ecc_point_to_bytes_compressed


class Ripple:

    _wif_prefix = h2b("21")
    _privkey_prefix = h2b("00")

    @classmethod
    def create_seed_from_mnemonic(cls, words):
        m = mnemonic.Mnemonic.normalize_string(words)
        passphrase = mnemonic.Mnemonic.normalize_string("")
        seed = PBKDF2(m, u'mnemonic' + passphrase, iterations=mnemonic.mnemonic.PBKDF2_ROUNDS,
                      macmodule=hmac,
                      digestmodule=hashlib.sha512).read(16)
        return seed

    @classmethod
    def secret_from_seed(cls, seed):
        # get first 16 bytes even if the seed is bigger
        secret = b2a_hashed_base58(cls._wif_prefix + seed[:16])
        return secret

    @classmethod
    def address_from_seed(cls, seed):
        secret = cls.secret_from_seed(seed)
        return get_ripple_from_secret(secret)

    @classmethod
    def address_from_pubkey(cls, pubkey):
        return get_ripple_from_pubkey(h2b(pubkey))

    @classmethod
    def pubkey_from_seed(cls, seed):
        print("seed", b2h(seed))
        root_key = root_key_from_seed(seed[:16])
        pubkey = fmt_hex(ecc_point_to_bytes_compressed(root_key.privkey.public_key.point,
                                                       pad=True))
        return pubkey

    @classmethod
    def privkey_from_seed(cls, seed):
        root_key = root_key_from_seed(seed[:16])
        privkey = fmt_hex(cls._privkey_prefix + to_bytes(root_key.privkey.secret_multiplier))
        return privkey