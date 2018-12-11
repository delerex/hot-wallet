from models.generate import generate_mnemonic, generate_encrypted_seed

mnemonic = generate_mnemonic()
print(f"mnemonic: {mnemonic}")
seed, btcxpub, ethxpub = generate_encrypted_seed(mnemonic, "password")
print(f"seed: {seed}")
print(f"btcpub: {btcxpub}")
print(f"ethpub: {ethxpub}")
