
from models.generate import generate_encrypted_seed, decrypt_seed
from models.network_type import NetworkType
from models.tron.tron_model import TronModel

words = ""
tron_model = TronModel(network_type=NetworkType.TESTNET)
seed = generate_encrypted_seed(words, password="pass")
seed = decrypt_seed(seed, "pass")
xpub = tron_model.generate_xpub(seed)
print(xpub)
addr = tron_model.get_addr_from_pub(xpub, 9, 0)
print(addr)

print()
priv, pub, addr = tron_model.get_priv_pub_addr(seed, 31, 0)
print(priv)
print(pub)
print(addr)
