from bitcoin import *

class CurrencyModel:

    def FloatToDecimal(self, value):
        return int(value * 10 ** self.decimals)


    def DecimalToFloat(self, value):
        return float(value / 10 ** self.decimals)


    def get_priv_pub_addr(self, root_seed, n):
        mk = bip32_master_key(root_seed)
        xpriv = bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(bip32_ckd(mk, 44 + 2 ** 31), 2 ** 31), 2 ** 31), 0), n)
        priv = bip32_extract_key(xpriv)
        pub = bip32_privtopub(xpriv)

        addr = privtoaddr(priv)
        return (priv, pub, addr)