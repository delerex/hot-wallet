from models.factory.currency_model_factory import CurrencyModelFactory
from models.generate import generate_mnemonic, generate_encrypted_seed, decrypt_seed

# mnemonic = generate_mnemonic()
from models.network_type import NetworkType

mnemonic = "giraffe light bone hockey infant open luggage era glimpse praise success ginger"
print(f"mnemonic:")
print(mnemonic)
encrypted_seed, btcxpub, ethxpub = generate_encrypted_seed(mnemonic, "qwer")
print(f"encrypted_seed: {encrypted_seed}")
seed = decrypt_seed(encrypted_seed, "qwer")
print(f"seed: {seed}")
print(f"btcpub: {btcxpub}")
print(f"ethpub: {ethxpub}")
