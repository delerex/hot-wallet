
class InputTransaction:

    def __init__(self, address, value, output, block_height, is_spent, priv_key=None):
        # {
        #     "address": "12vimHE11zzkYGTxtmws1kJiW5MV3FhBMh",
        #     "value": 1391504,
        #     "output": "3977a3e9bf55d1ea45fc9fda209f4b6d0c61c483a5315f9d84cdb0c3c2a0b139:0",
        #     "block_height": 551133,
        #     "is_spent": True
        #   },
        self.address = address
        self.value = value
        self.output = output
        self.block_height = block_height
        self.is_spent = is_spent
        self.priv_key = priv_key

    def to_dict(self):
        return {
            "address": self.address,
            "value": self.value,
            "output": self.output,
            "block_height": self.block_height,
            "is_spent": self.is_spent
        }
